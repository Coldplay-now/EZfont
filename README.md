# QuickFont (EZfont) - AI-Powered Font Generator

<div align="center">

![QuickFont Logo](https://via.placeholder.com/200x60/1a1a1a/FFFFFF?text=QuickFont)

**Create professional fonts in minutes with AI**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

</div>

## 🎨 Overview

QuickFont (also known as EZfont) is an AI-powered font generation tool that allows users to create professional-grade original fonts in minutes. Simply describe your desired font style, and our AI will analyze your requirements and generate a custom TrueType font file.

## ✨ Features

- 🤖 **AI-Powered Design**: Uses DeepSeek AI to analyze user requirements and generate detailed font specifications
- 🎯 **Parameterized Generation**: Creates fonts based on design parameters (strokeWidth, contrast, terminals, corners, etc.)
- 📐 **Professional Quality**: Generates valid TrueType (.ttf) fonts compatible with macOS, Windows, and Linux
- 🎨 **Visual Preview**: Real-time preview with customizable text, size, weight, and spacing
- 📚 **Font Management**: View, preview, download, and manage all your generated fonts
- 🔧 **Easy to Use**: Simple web interface - no design experience required

## 🚀 Quick Start

### Prerequisites

- **Node.js** >= 16.0.0
- **Python** >= 3.8
- **npm** or **yarn**
- **DeepSeek API Key** (get one at [DeepSeek](https://platform.deepseek.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Coldplay-now/EZfont.git
   cd EZfont
   ```

2. **Configure API Key**
   ```bash
   cp config/config.json.example config/config.json
   # Edit config/config.json and add your DeepSeek API key
   ```

3. **Install dependencies**
   ```bash
   # Install frontend dependencies
   cd frontend && npm install && cd ..
   
   # Install backend dependencies
   cd backend && npm install && cd ..
   
   # Install Python dependencies
   cd font-generator && pip install -r requirements.txt && cd ..
   ```

4. **Start the services**
   ```bash
   # Start both frontend and backend
   ./start.sh
   ```

5. **Access the application**
   - Frontend: http://localhost:5174
   - Backend API: http://localhost:3001
   - Health Check: http://localhost:3001/health

## 📖 Usage

### Creating a Font

1. Navigate to **AI Generator** page
2. Enter your font description (e.g., "Generate a modern geometric font, clean and minimalist")
3. Select font type, weight, and character set
4. Click **Generate My Font**
5. Wait for AI analysis and font generation
6. Preview and download your font!

### Example Descriptions

Check out [`FONT_STYLE_PROMPTS.md`](./FONT_STYLE_PROMPTS.md) for 30+ example descriptions that produce visually distinct fonts.

**Quick examples**:
- "Generate an extremely delicate geometric font, elegant and lightweight, uniform stroke width, modern minimalist style"
- "Generate a super bold black font, thick and eye-catching, thin horizontal and thick vertical strokes, strong impact"
- "Generate a fashionable angled font, sharp stroke ends, pointed design, dynamic and avant-garde"

## 🏗️ Project Structure

```
QuickFont/
├── frontend/              # React + TypeScript frontend
│   ├── src/
│   │   ├── pages/        # Page components
│   │   ├── components/   # Reusable components
│   │   ├── services/    # API services
│   │   └── types/       # TypeScript types
│   └── package.json
├── backend/              # Node.js + Express backend
│   ├── src/
│   │   ├── routes/      # API routes
│   │   ├── services/    # Business logic
│   │   ├── database/    # SQLite database
│   │   └── index.ts     # Entry point
│   └── package.json
├── font-generator/       # Python font generation
│   ├── generator.py     # Main generator
│   ├── glyph_designer.py # Glyph design logic
│   ├── bezier_utils.py  # Bezier curve utilities
│   └── requirements.txt
├── shared/              # Shared type definitions
├── config/             # Configuration files
├── output/             # Generated font files (gitignored)
├── logs/               # Application logs (gitignored)
└── docs/               # Documentation files
```

## 🎯 Design Parameters

The system uses various design parameters to create unique fonts:

- **strokeWidth** (55-125): Base stroke width - from extremely thin to super bold
- **contrast** (none/low/medium/high): Horizontal vs vertical stroke contrast
- **terminals** (straight/curved/angled): Stroke end styles
- **corners** (sharp/rounded/soft): Corner treatment
- **aperture** (closed/semi-open/open): Open character aperture
- **axis** (vertical/angled/mixed): Stroke axis orientation
- **stress** (none/vertical/angled/reverse): Stroke stress distribution

## 📚 Documentation

- [`FONT_STYLE_PROMPTS.md`](./FONT_STYLE_PROMPTS.md) - 30+ font style descriptions
- [`FONT_PREVIEW_GUIDE.md`](./FONT_PREVIEW_GUIDE.md) - How to preview fonts
- [`API_CONFIG.md`](./API_CONFIG.md) - API configuration guide
- [`USAGE_GUIDE.md`](./USAGE_GUIDE.md) - Detailed usage instructions
- [`PHASE2_IMPLEMENTATION.md`](./PHASE2_IMPLEMENTATION.md) - Technical implementation details

## 🛠️ Development

### Running in Development Mode

```bash
# Backend (port 3001)
cd backend && npm run dev

# Frontend (port 5174)
cd frontend && npm run dev
```

### Stopping Services

```bash
./stop.sh
```

### Database

The application uses SQLite for storing font metadata. Database file: `backend/fonts.db`

## 🧪 Testing

Generate fonts with different styles to see the visual differences:

```bash
# Test font generation
cd font-generator
python3 generator.py --spec test_spec.json --output /tmp --font-id test_font
```

## 📝 API Endpoints

- `GET /api/fonts` - List all fonts
- `GET /api/fonts/:fontId` - Get font details
- `DELETE /api/fonts/:fontId` - Delete a font
- `GET /api/font/:fontId/download` - Download font file
- `POST /api/analyze-requirements` - Analyze user requirements (AI)
- `POST /api/generate-font` - Generate font file

## 🔧 Configuration

Edit `config/config.json`:

```json
{
  "deepseek": {
    "apiKey": "your-api-key-here",
    "apiUrl": "https://api.deepseek.com/v1/chat/completions"
  },
  "corsOrigin": "http://localhost:5174"
}
```

## 🐛 Troubleshooting

### Font Generation Fails

- Check DeepSeek API key is valid
- Ensure Python dependencies are installed: `pip install fonttools`
- Check backend logs: `tail -f logs/backend.log`

### Fonts Look the Same

- Use more extreme descriptions (see `FONT_STYLE_PROMPTS.md`)
- Ensure AI prompt optimization is enabled
- Check font parameters in specification page

### Network Errors

- Verify backend is running: `curl http://localhost:3001/health`
- Check CORS configuration
- Ensure frontend is on port 5174

## 📊 Current Status

### ✅ Completed Features

- [x] AI-powered requirement analysis
- [x] Parameterized font generation
- [x] TrueType font file generation
- [x] Font preview and management
- [x] 26 uppercase letters (A-Z)
- [x] 26 lowercase letters (a-z)
- [x] 10 digits (0-9)
- [x] Basic punctuation marks
- [x] Visual parameter application (terminals, corners, contrast)

### 🚧 In Progress

- [ ] Extended punctuation support
- [ ] Variable font support
- [ ] Kerning optimization
- [ ] More parameter applications

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Built with [React](https://react.dev/)
- Powered by [DeepSeek AI](https://www.deepseek.com/)
- Font generation using [fontTools](https://github.com/fonttools/fonttools)

## 📮 Contact

- Repository: https://github.com/Coldplay-now/EZfont
- Issues: https://github.com/Coldplay-now/EZfont/issues

---

**Made with ❤️ by the QuickFont team**
