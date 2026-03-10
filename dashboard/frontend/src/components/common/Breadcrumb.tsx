import { Box, Breadcrumbs, Link, Typography } from '@mui/material';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import { NavigateNext as NavigateNextIcon, Home as HomeIcon } from '@mui/icons-material';

interface BreadcrumbItem {
  label: string;
  path?: string;
}

/**
 * Maps route paths to human-readable labels
 */
const routeLabels: Record<string, string> = {
  'dashboard': 'Dashboard',
  'suites': 'Test Suites',
  'cases': 'Test Cases',
  'executions': 'Executions',
  'integrations': 'Integrations',
  'self-healing': 'Self-Healing',
  'billing': 'Billing',
  'settings': 'Settings',
};

/**
 * Dynamic breadcrumb component that auto-generates from current route
 */
export default function DynamicBreadcrumb() {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  // Don't show breadcrumb on root or landing page
  if (pathnames.length === 0 || location.pathname === '/') {
    return null;
  }

  /**
   * Generate breadcrumb items from path
   */
  const getBreadcrumbItems = (): BreadcrumbItem[] => {
    const items: BreadcrumbItem[] = [];

    pathnames.forEach((value, index) => {
      const isLast = index === pathnames.length - 1;
      const path = `/${pathnames.slice(0, index + 1).join('/')}`;

      // Handle dynamic routes (e.g., :suiteId)
      const isDynamicRoute = /^\d+$/.test(value) || value.includes(':');

      if (isDynamicRoute && index > 0) {
        // For dynamic routes, append to parent label
        const parentLabel = routeLabels[pathnames[index - 1]] || pathnames[index - 1];
        items.push({
          label: `${parentLabel} Details`,
          path: isLast ? undefined : path,
        });
      } else {
        items.push({
          label: routeLabels[value] || value.charAt(0).toUpperCase() + value.slice(1),
          path: isLast ? undefined : path,
        });
      }
    });

    return items;
  };

  const breadcrumbItems = getBreadcrumbItems();

  return (
    <Box sx={{ mb: 2, mt: 1 }}>
      <Breadcrumbs
        separator={<NavigateNextIcon fontSize="small" />}
        aria-label="breadcrumb"
        sx={{
          '& .MuiBreadcrumbs-separator': {
            color: 'text.secondary',
          },
        }}
      >
        {/* Home Link */}
        <Link
          component={RouterLink}
          to="/dashboard"
          color="inherit"
          sx={{
            display: 'flex',
            alignItems: 'center',
            textDecoration: 'none',
            '&:hover': {
              textDecoration: 'underline',
            },
          }}
        >
          <HomeIcon sx={{ mr: 0.5, fontSize: 18 }} />
          Home
        </Link>

        {/* Dynamic Breadcrumb Items */}
        {breadcrumbItems.map((item, index) => {
          const isLast = index === breadcrumbItems.length - 1;

          return isLast || !item.path ? (
            <Typography
              key={item.path || index}
              color="text.primary"
              sx={{ fontWeight: 500 }}
            >
              {item.label}
            </Typography>
          ) : (
            <Link
              key={item.path}
              component={RouterLink}
              to={item.path}
              color="inherit"
              sx={{
                textDecoration: 'none',
                '&:hover': {
                  textDecoration: 'underline',
                },
              }}
            >
              {item.label}
            </Link>
          );
        })}
      </Breadcrumbs>
    </Box>
  );
}
