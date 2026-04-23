@echo off
REM Setup script for Vercel deployment

echo Installing Git if not present...
winget install Git.Git

echo Initializing git repository...
git init

echo Adding files...
git add -A

echo Creating initial commit...
git config user.name "Developer"
git config user.email "dev@example.com"
git commit -m "Initial commit: Vercel-ready API setup"

echo.
echo ✓ Git is ready!
echo.
echo Next steps:
echo 1. Create repository on GitHub/GitLab
echo 2. Add remote: git remote add origin <your-repo-url>
echo 3. Push: git push -u origin main
echo 4. Deploy to Vercel: npx vercel
echo.
pause
