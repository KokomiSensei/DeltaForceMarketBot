# Bot Configuration Frontend

A comprehensive frontend visualization service for managing Python bot configurations.

## Features

- **Bot Control Panel**: Start/stop bot operations with real-time status
- **Configuration Management**: Create, edit, and delete bot configurations
- **Real-time Updates**: Live configuration updates with partial and full replacement
- **Mock Backend**: Complete API simulation for development and testing
- **Responsive Design**: Works on desktop and mobile devices

## Project Structure

\`\`\`
├── app/
│   ├── api/                    # Mock backend API routes
│   │   ├── bot/               # Bot control endpoints
│   │   └── configs/           # Configuration management endpoints
│   ├── page.tsx               # Main dashboard
│   └── layout.tsx             # App layout
├── components/
│   ├── bot-config-form.tsx    # Configuration form component
│   ├── bot-control-panel.tsx  # Bot start/stop controls
│   └── config-manager.tsx     # Configuration CRUD interface
├── lib/
│   └── api-client.ts          # API client for backend communication
├── types/
│   └── bot-config.ts          # TypeScript interfaces
└── .env.example               # Environment configuration template
\`\`\`

## Getting Started

### Development

1. **Install dependencies**:
   \`\`\`bash
   npm install
   \`\`\`

2. **Set up environment**:
   \`\`\`bash
   cp .env.example .env.local
   \`\`\`

3. **Start development server**:
   \`\`\`bash
   npm run dev
   \`\`\`

4. **Access the application**:
   Open [http://localhost:3000](http://localhost:3000)

### Production Deployment

1. **Configure backend URL**:
   Update `NEXT_PUBLIC_BACKEND_URL` in your environment to point to your Python backend:
   \`\`\`env
   NEXT_PUBLIC_BACKEND_URL=https://your-python-backend.com
   \`\`\`

2. **Deploy to Vercel**:
   - Push to GitHub
   - Connect to Vercel
   - Set environment variables in Vercel dashboard
   - Deploy

## API Endpoints

### Bot Management
- `GET /api/bot/config` - Get current bot configuration
- `POST /api/bot/config` - Set complete bot configuration
- `PATCH /api/bot/config` - Partially update bot configuration
- `POST /api/bot/start` - Start the bot
- `POST /api/bot/stop` - Stop the bot

### Configuration Management
- `GET /api/configs` - Get all saved configurations
- `POST /api/configs` - Create new configuration
- `PUT /api/configs/{name}` - Update existing configuration
- `DELETE /api/configs/{name}` - Delete configuration
- `POST /api/configs/{oldName}/rename/{newName}` - Rename configuration

## Configuration Schema

\`\`\`typescript
interface BotConfig {
  name: string;
  lowest_price: number;
  volume: number;
  screenshot_delay: number;
  debug_mode: boolean;
  target_schema_index: number;
}

interface BotConfigOpt {
  name?: string;
  lowest_price?: number;
  volume?: number;
  screenshot_delay?: number;
  debug_mode?: boolean;
  target_schema_index?: number;
}
\`\`\`

## Backend Integration

The frontend is designed to work with your Python backend. To integrate:

1. **Update API client**: Modify `lib/api-client.ts` to point to your Python backend
2. **Environment setup**: Set `NEXT_PUBLIC_BACKEND_URL` to your backend URL
3. **CORS configuration**: Ensure your Python backend allows requests from your frontend domain

### Python Backend Requirements

Your Python backend should implement the same API endpoints as defined in `bot-config-opt.py`:

- FastAPI or Flask with the same route structure
- CORS enabled for frontend domain
- JSON request/response format
- Error handling with appropriate HTTP status codes

## Development vs Production

- **Development**: Uses mock API routes in `app/api/` for standalone testing
- **Production**: Connects to your actual Python backend via `NEXT_PUBLIC_BACKEND_URL`

The mock backend provides the same interface as your Python backend, making development and testing seamless.
