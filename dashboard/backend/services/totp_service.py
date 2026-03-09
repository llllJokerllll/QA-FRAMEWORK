"""
Two-Factor Authentication Service

Provides TOTP-based 2FA:
- TOTP generation and verification
- QR code generation
- Backup codes
- Recovery flow
"""

import pyotp
import qrcode
import io
import base64
import secrets
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
import structlog

logger = structlog.get_logger()

Base = declarative_base()


class TwoFactorAuth(Base):
    """Two-factor authentication model"""
    __tablename__ = "two_factor_auth"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    secret = Column(String(32), nullable=False)
    is_enabled = Column(Boolean, default=False)
    backup_codes = Column(String(500), nullable=True)  # JSON array of hashed codes
    created_at = Column(DateTime, nullable=False)
    last_used_at = Column(DateTime, nullable=True)


class TOTPService:
    """TOTP-based 2FA service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def generate_secret(self) -> str:
        """Generate new TOTP secret"""
        return pyotp.random_base32()
    
    def get_totp(self, secret: str) -> pyotp.TOTP:
        """Get TOTP instance"""
        return pyotp.TOTP(secret)
    
    def verify_code(self, secret: str, code: str) -> bool:
        """Verify TOTP code"""
        totp = self.get_totp(secret)
        return totp.verify(code, valid_window=1)  # Allow 1 step drift (30 seconds)
    
    def generate_qr_code(
        self,
        secret: str,
        email: str,
        issuer: str = "QA-FRAMEWORK"
    ) -> str:
        """
        Generate QR code for TOTP setup
        
        Returns:
            Base64-encoded PNG image
        """
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name=issuer
        )
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes"""
        codes = []
        for _ in range(count):
            code = secrets.token_hex(4).upper()  # 8-character hex code
            codes.append(code)
        return codes
    
    def hash_backup_code(self, code: str) -> str:
        """Hash backup code for storage"""
        import hashlib
        return hashlib.sha256(code.encode()).hexdigest()
    
    def verify_backup_code(self, hashed_code: str, code: str) -> bool:
        """Verify backup code"""
        return hashed_code == self.hash_backup_code(code)
    
    async def setup_2fa(
        self,
        user_id: int
    ) -> dict:
        """
        Setup 2FA for user
        
        Returns:
            Dict with secret, qr_code, and backup_codes
        """
        from datetime import datetime
        import json
        
        # Generate secret
        secret = self.generate_secret()
        
        # Generate backup codes
        backup_codes = self.generate_backup_codes()
        hashed_codes = [self.hash_backup_code(code) for code in backup_codes]
        
        # Create 2FA record (not enabled yet)
        two_factor = TwoFactorAuth(
            user_id=user_id,
            secret=secret,
            is_enabled=False,
            backup_codes=json.dumps(hashed_codes),
            created_at=datetime.utcnow()
        )
        
        self.db.add(two_factor)
        await self.db.commit()
        
        logger.info("2FA setup initiated", user_id=user_id)
        
        return {
            "secret": secret,
            "backup_codes": backup_codes,  # Only show once!
            "message": "Verify code to enable 2FA"
        }
    
    async def enable_2fa(
        self,
        user_id: int,
        code: str
    ) -> bool:
        """Enable 2FA after verification"""
        from sqlalchemy import select
        
        result = await self.db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.user_id == user_id)
        )
        two_factor = result.scalar_one_or_none()
        
        if not two_factor:
            return False
        
        # Verify code
        if not self.verify_code(two_factor.secret, code):
            return False
        
        # Enable 2FA
        two_factor.is_enabled = True
        await self.db.commit()
        
        logger.info("2FA enabled", user_id=user_id)
        
        return True
    
    async def verify_2fa(
        self,
        user_id: int,
        code: str
    ) -> bool:
        """Verify 2FA code or backup code"""
        from sqlalchemy import select
        from datetime import datetime
        import json
        
        result = await self.db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.user_id == user_id)
        )
        two_factor = result.scalar_one_or_none()
        
        if not two_factor or not two_factor.is_enabled:
            return True  # 2FA not enabled, allow
        
        # Try TOTP code
        if self.verify_code(two_factor.secret, code):
            two_factor.last_used_at = datetime.utcnow()
            await self.db.commit()
            return True
        
        # Try backup code
        hashed_codes = json.loads(two_factor.backup_codes) if two_factor.backup_codes else []
        for i, hashed_code in enumerate(hashed_codes):
            if self.verify_backup_code(hashed_code, code):
                # Remove used backup code
                hashed_codes.pop(i)
                two_factor.backup_codes = json.dumps(hashed_codes)
                two_factor.last_used_at = datetime.utcnow()
                await self.db.commit()
                
                logger.info("Backup code used", user_id=user_id, codes_remaining=len(hashed_codes))
                
                return True
        
        return False
    
    async def disable_2fa(
        self,
        user_id: int,
        code: str
    ) -> bool:
        """Disable 2FA"""
        # Verify code first
        if not await self.verify_2fa(user_id, code):
            return False
        
        from sqlalchemy import select
        
        result = await self.db.execute(
            select(TwoFactorAuth).where(TwoFactorAuth.user_id == user_id)
        )
        two_factor = result.scalar_one_or_none()
        
        if two_factor:
            await self.db.delete(two_factor)
            await self.db.commit()
            
            logger.info("2FA disabled", user_id=user_id)
        
        return True
    
    async def is_2fa_enabled(self, user_id: int) -> bool:
        """Check if 2FA is enabled for user"""
        from sqlalchemy import select
        
        result = await self.db.execute(
            select(TwoFactorAuth).where(
                TwoFactorAuth.user_id == user_id,
                TwoFactorAuth.is_enabled == True
            )
        )
        return result.scalar_one_or_none() is not None
