# Emotion Style Explorer — fal.ai prototype

This small prototype wires the existing `index.html` UI to a simple Flask backend that calls the fal.ai image-generation API.

## Local Development

Quick start (Windows / PowerShell):

1. Create a virtualenv and install dependencies

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Create `.env` file in project root with your fal.ai API key

```
FAL_API_KEY=sk-...
FAL_MODEL_ID=fal-ai/flux/dev
```

3. Run the backend

```powershell
python app.py
```

4. Open http://localhost:7860 in your browser and use the UI.

## Deploy to Vercel

### Step 1: Create a Vercel account (Free)
- Go to [vercel.com](https://vercel.com)
- Sign up with GitHub, GitLab, or email

### Step 2: Push your project to GitHub (optional but recommended)
```bash
git init
git add .
git commit -m "Initial commit: emotion style explorer with fal.ai"
git remote add origin https://github.com/YOUR_USERNAME/emotion-project.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy from Vercel Dashboard
**Option A: From GitHub**
1. In Vercel dashboard, click "New Project"
2. Select your GitHub repo (`emotion-project`)
3. Click "Import"
4. Under "Environment Variables", add:
   - `FAL_API_KEY` = your fal.ai API key (get from https://fal.ai/dashboard/keys)
   - `FAL_MODEL_ID` = `fal-ai/flux/dev` (or another model you prefer)
5. Click "Deploy"

**Option B: Using Vercel CLI**
```powershell
npm i -g vercel
vercel login
vercel --prod
# Follow prompts to set environment variables
```

### Step 4: Test your deployment
- Vercel will give you a URL like `https://emotion-project-xxx.vercel.app`
- Open it and click Generate to test

## Notes

- The `app.py` code expects the fal.ai response to include `images` array with `url` field (standard fal.ai format).
- Keep your API key secret — use Vercel's environment variables UI, never commit `.env` to git.
- Vercel free tier gives you 100 function invocations per day; each image generation = 1 invocation.
- For long-running or heavy models, consider using fal.ai's Queue API + webhooks instead of synchronous calls.

