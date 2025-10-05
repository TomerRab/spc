# SPC Client - Frontend Application

Modern React-based web application for creating GitLab repositories with pre-configured templates, CI/CD pipelines, and deployment configurations.

## Tech Stack

- **Framework**: React 18.3 with TypeScript 5.5
- **Build Tool**: Vite 5.4 with SWC for fast compilation
- **UI Framework**: shadcn/ui (Radix UI primitives)
- **Styling**: Tailwind CSS 3.4 with custom configuration
- **Form Management**: React Hook Form 7.53 with Zod validation
- **State Management**: TanStack Query (React Query) 5.56
- **Routing**: React Router DOM 6.26
- **Icons**: Lucide React
- **Notifications**: Sonner toast library

## Features

### Authentication
- **GitLab OAuth 2.0 Integration**: Secure authentication flow
- **Token Management**: Automatic token storage and validation
- **Protected Routes**: Route guards for authenticated pages
- **Auth Context**: Global authentication state management

### Project Creation
- **Multi-step Form**: Guided project creation workflow
- **Real-time Validation**: Form validation with Zod schemas
- **Group Selection**: Search and select GitLab groups with debounced search
- **Stack Selection**: Choose from multiple technology stacks
- **Cluster Configuration**: Configure deployment clusters and environments
- **Delivery Options**: Separate delivery repository configuration

### User Interface
- **Responsive Design**: Mobile-first responsive layout
- **Dark Mode Support**: Theme switching capability
- **Accessible Components**: ARIA-compliant UI components
- **Loading States**: Skeleton loaders and progress indicators
- **Error Handling**: User-friendly error messages and dialogs
- **Toast Notifications**: Non-intrusive success/error notifications

## Project Structure

```
spc-client/
├── public/                      # Static assets
├── src/
│   ├── components/
│   │   ├── auth/               # Authentication components
│   │   │   ├── ProtectedRoute.tsx
│   │   │   └── LoginButton.tsx
│   │   ├── forms/              # Form components
│   │   │   ├── ProjectForm.tsx
│   │   │   ├── ProjectSuccessDialog.tsx
│   │   │   └── ClusterForm.tsx
│   │   ├── project-creation/   # Project creation flow
│   │   │   ├── ProjectTypeSelector.tsx
│   │   │   ├── StackSelector.tsx
│   │   │   └── ReviewStep.tsx
│   │   ├── selectors/          # Selection components
│   │   │   ├── GroupSelector.tsx
│   │   │   └── StackCombobox.tsx
│   │   └── ui/                 # shadcn/ui components
│   │       ├── button.tsx
│   │       ├── input.tsx
│   │       ├── form.tsx
│   │       └── ... (30+ components)
│   ├── contexts/
│   │   └── AuthContext.tsx     # Global auth state
│   ├── hooks/
│   │   ├── useAuth.ts          # Authentication hook
│   │   ├── useGroups.ts        # Groups fetching hook
│   │   └── useDebounce.ts      # Debounce utility hook
│   ├── pages/
│   │   ├── Index.tsx           # Landing page
│   │   ├── Login.tsx           # OAuth callback handler
│   │   ├── CreateProject.tsx   # Main project creation page
│   │   └── NotFound.tsx        # 404 page
│   ├── services/
│   │   ├── auth.service.ts     # Authentication API calls
│   │   ├── groups.service.ts   # Groups API calls
│   │   ├── projects.service.ts # Project creation API calls
│   │   └── index.ts            # Service exports
│   ├── schemas/
│   │   └── projectSchema.ts    # Zod validation schemas
│   ├── types/
│   │   ├── gitlab.ts           # GitLab type definitions
│   │   └── projectForm.ts      # Form type definitions
│   ├── config/
│   │   ├── env.ts              # Environment configuration
│   │   └── project.ts          # Project constants
│   ├── utils/
│   │   ├── errorHandler.ts     # Error handling utilities
│   │   └── cn.ts               # Class name utility
│   ├── lib/
│   │   └── utils.ts            # Shared utilities
│   ├── constants/
│   │   └── index.ts            # Application constants
│   ├── App.tsx                 # Root component
│   ├── main.tsx                # Application entry point
│   └── index.css               # Global styles
├── .env.example                # Environment variables template
├── vite.config.ts              # Vite configuration
├── tailwind.config.ts          # Tailwind CSS configuration
├── tsconfig.json               # TypeScript configuration
└── package.json                # Dependencies and scripts
```

## Installation

### Prerequisites
- Node.js 18.x or higher
- npm or yarn package manager
- Access to SPC backend API
- GitLab OAuth application credentials

### Setup

1. **Clone the repository**
   ```bash
   cd spc-client
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your configuration:
   ```env
   # Backend API URL
   VITE_API_BASE_URL=http://localhost:8000

   # GitLab OAuth Configuration
   VITE_GITLAB_CLIENT_ID=your_gitlab_client_id
   VITE_GITLAB_REDIRECT_URI=http://localhost:8080/callback

   # Application Configuration
   VITE_DEFAULT_BRANCH=main
   VITE_DEFAULT_VISIBILITY=private

   # Search Configuration
   VITE_SEARCH_DEBOUNCE_MS=300
   VITE_SEARCH_MIN_CHARS=3
   VITE_COMMON_GROUPS_LIMIT=200
   VITE_SEARCH_RESULTS_LIMIT=50
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

   Application will be available at `http://localhost:8080`

## Development

### Available Scripts

- **`npm run dev`**: Start development server with hot reload
- **`npm run build`**: Build production bundle
- **`npm run build:dev`**: Build development bundle
- **`npm run preview`**: Preview production build locally
- **`npm run lint`**: Run ESLint for code quality

### Development Workflow

1. **Start the backend API** (required for full functionality)
2. **Run development server**: `npm run dev`
3. **Make changes**: Hot reload will update automatically
4. **Lint code**: Run `npm run lint` before committing
5. **Test builds**: Use `npm run build` to verify production build

### Code Style

- **TypeScript**: Strict mode enabled
- **ESLint**: Configured with React and TypeScript rules
- **Formatting**: Consistent code formatting enforced
- **Component Structure**: Functional components with hooks
- **File Naming**:
  - Components: PascalCase (e.g., `ProjectForm.tsx`)
  - Utilities: camelCase (e.g., `errorHandler.ts`)
  - Types: camelCase with `.ts` extension

### Adding New Components

1. **shadcn/ui components**:
   ```bash
   npx shadcn-ui@latest add [component-name]
   ```

2. **Custom components**:
   - Place in appropriate directory (`components/forms`, `components/project-creation`, etc.)
   - Export from `index.ts` if needed
   - Add TypeScript types
   - Include PropTypes or type definitions

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |
| `VITE_GITLAB_CLIENT_ID` | GitLab OAuth client ID | - |
| `VITE_GITLAB_REDIRECT_URI` | OAuth redirect URI | `http://localhost:8080/callback` |
| `VITE_DEFAULT_BRANCH` | Default Git branch name | `main` |
| `VITE_DEFAULT_VISIBILITY` | Default repo visibility | `private` |
| `VITE_SEARCH_DEBOUNCE_MS` | Search input debounce delay | `300` |
| `VITE_SEARCH_MIN_CHARS` | Minimum chars for search | `3` |
| `VITE_COMMON_GROUPS_LIMIT` | Max groups to fetch | `200` |
| `VITE_SEARCH_RESULTS_LIMIT` | Max search results | `50` |

### Tailwind Configuration

Custom theme extensions in `tailwind.config.ts`:
- Custom colors matching shadcn/ui theme
- Custom animations and keyframes
- Typography plugin enabled
- Container utilities configured

### Vite Configuration

- **Port**: 8080 (development)
- **Proxy**: Not configured (direct API calls)
- **Build Target**: ES2020
- **Code Splitting**: Automatic for optimal bundle size
- **Assets**: Inlined if < 4KB

## API Integration

### Service Layer

All API calls are abstracted into service modules:

```typescript
// services/projects.service.ts
export const projectsService = {
  createProject: async (token: string, data: ProjectFormData) => {
    const response = await fetch(`${config.API_BASE_URL}/generate-repo`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  },
};
```

### Using React Query

```typescript
const { mutate, isLoading, error } = useMutation({
  mutationFn: (data: ProjectFormData) =>
    projectsService.createProject(token, data),
  onSuccess: (data) => {
    toast.success('Project created successfully!');
  },
  onError: (error) => {
    toast.error('Failed to create project');
  },
});
```

## State Management

### Authentication Context

Global authentication state using React Context:

```typescript
const { token, isAuthenticated, login, logout } = useAuth();
```

### TanStack Query

Server state management for:
- Groups fetching with caching
- Project creation mutations
- Automatic refetching and cache invalidation

### Form State

Local form state with React Hook Form:
- Form validation with Zod schemas
- Error handling and display
- Dirty field tracking
- Submit handling

## Building for Production

### Build Process

```bash
npm run build
```

Output in `dist/` directory:
- Optimized and minified JavaScript
- CSS extracted and minimized
- Assets with content hashing
- Source maps for debugging

### Build Optimization

- **Tree Shaking**: Unused code removed
- **Code Splitting**: Lazy loading for routes
- **Asset Optimization**: Images and fonts optimized
- **Compression**: Gzip-ready output

### Deployment

#### Static Hosting (Vercel, Netlify, etc.)

```bash
npm run build
# Deploy dist/ directory
```

#### Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
docker build -t spc-client .
docker run -p 80:80 spc-client
```

#### Environment-Specific Builds

For different environments, use `.env.production` or `.env.staging`:

```bash
npm run build -- --mode production
npm run build -- --mode staging
```

## Troubleshooting

### Common Issues

**OAuth Redirect Loop**
- Verify `VITE_GITLAB_REDIRECT_URI` matches GitLab app settings
- Check browser console for errors
- Clear localStorage and cookies

**API Connection Errors**
- Ensure backend is running on correct port
- Check `VITE_API_BASE_URL` in `.env`
- Verify CORS configuration on backend

**Build Failures**
- Clear `node_modules/` and reinstall: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf node_modules/.vite`
- Check TypeScript errors: `npx tsc --noEmit`

**Performance Issues**
- Enable React DevTools Profiler
- Check bundle size: `npm run build` and inspect output
- Consider lazy loading heavy components

### Debug Mode

Enable verbose logging by adding to console:
```javascript
localStorage.setItem('debug', 'spc:*');
```

## Contributing

1. Follow existing code structure and patterns
2. Add TypeScript types for all new code
3. Use shadcn/ui components when possible
4. Keep components small and focused
5. Add proper error handling
6. Test on multiple browsers
7. Ensure accessibility compliance

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari, Chrome for Android

## License

MIT License
