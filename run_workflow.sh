#!/bin/bash

# ============================================
# Quick Start Script for Catalyst AI E2E Test
# ============================================

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Catalyst AI - End-to-End Workflow Test Launcher        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ ERROR: .env file not found!"
    echo "Please create .env with required API keys"
    exit 1
fi

# Check if uploads folder exists
if [ ! -d "uploads" ]; then
    echo "⚠️  WARNING: uploads/ folder not found"
    echo "Creating uploads/ folder for you..."
    mkdir -p uploads
fi

echo ""
echo "Choose an option:"
echo ""
echo "1️⃣  DRY RUN (Test workflow, no posting, no video generation)"
echo "2️⃣  FULL WORKFLOW (Generate content and post, no video)"
echo "3️⃣  FULL WORKFLOW + VIDEO (Generate everything, use SORA credits)"
echo "4️⃣  Exit"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🧪 Starting DRY RUN..."
        echo ""
        python3 end_to_end_workflow.py --dry-run
        ;;
    2)
        echo ""
        echo "🚀 Starting FULL WORKFLOW (no video)..."
        echo ""
        python3 end_to_end_workflow.py
        ;;
    3)
        echo ""
        echo "⚠️  WARNING: This will generate VIDEO and use SORA credits!"
        echo ""
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            echo ""
            echo "🎬 Starting FULL WORKFLOW with VIDEO GENERATION..."
            echo ""
            python3 end_to_end_workflow.py --generate-video
        else
            echo "Cancelled."
        fi
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice"
        ;;
esac

echo ""
echo "Check workflow_results_final.json for detailed results"
echo ""
