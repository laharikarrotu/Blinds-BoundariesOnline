#!/bin/bash
# Move outdated documentation to archive

cd "$(dirname "$0")/../docs"

# Create archive directory
mkdir -p archive

# Move outdated docs to archive
echo "Moving outdated documentation to archive/..."

# Azure setup docs (completed)
mv AZURE_*.md archive/ 2>/dev/null

# Vercel setup docs (completed)
mv VERCEL_*.md archive/ 2>/dev/null

# Quick setup guides (superseded)
mv QUICK_*.md archive/ 2>/dev/null

# Step-by-step guides (superseded by main guides)
mv STEP_*.md archive/ 2>/dev/null
mv DEPLOY_*.md archive/ 2>/dev/null

# Fix guides (issues resolved)
mv FIX_*.md archive/ 2>/dev/null

# MCP setup docs (completed)
mv MCP_*.md archive/ 2>/dev/null
mv CURSOR_*.md archive/ 2>/dev/null
mv GET_*.md archive/ 2>/dev/null

# GitHub/Azure status docs (historical)
mv GITHUB_*.md archive/ 2>/dev/null
mv IDE_*.md archive/ 2>/dev/null

# Integration/connection docs (completed)
mv IMPORTANT_*.md archive/ 2>/dev/null
mv INTEGRATION_*.md archive/ 2>/dev/null
mv CONNECTION*.md archive/ 2>/dev/null
mv CONFIGURATION*.md archive/ 2>/dev/null
mv EXISTING*.md archive/ 2>/dev/null

# Recruiter/docs (temporary)
mv RECRUITER*.md archive/ 2>/dev/null

# Tech stack docs (redundant)
mv TECH_STACK*.md archive/ 2>/dev/null
mv REDUNDANT*.md archive/ 2>/dev/null
mv STORAGE*.md archive/ 2>/dev/null
mv ENHANCEMENT*.md archive/ 2>/dev/null
mv PROJECT_STATUS*.md archive/ 2>/dev/null

echo "✅ Documentation archived"
echo ""
echo "Essential docs kept:"
ls -1 *.md 2>/dev/null | head -10

