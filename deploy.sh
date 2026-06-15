#!/bin/bash
# ============================================================================
# MeshClean Debugger - Deploy Script
# Quick setup and deployment for all platforms
# ============================================================================

set -e

echo "=========================================="
echo "MeshClean Debugger - Deployment Script"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_step() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# ============================================================================
# MENU
# ============================================================================

echo "Select deployment option:"
echo "1) Setup & Run Locally"
echo "2) Build & Run Docker"
echo "3) Verify All Components"
echo "4) Initialize GitHub Repository"
echo "5) Test All Tasks"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo ""
        print_step "Setting up local environment..."
        
        # Check Python
        if ! command -v python3 &> /dev/null; then
            print_warning "Python 3 not found. Please install Python 3.11+"
            exit 1
        fi
        print_success "Python found: $(python3 --version)"
        
        # Create venv
        if [ ! -d "venv" ]; then
            print_step "Creating virtual environment..."
            python3 -m venv venv
            print_success "Virtual environment created"
        fi
        
        # Activate venv
        print_step "Activating virtual environment..."
        source venv/bin/activate
        
        # Install dependencies
        print_step "Installing dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "Dependencies installed"
        
        # Run app
        echo ""
        print_success "Starting MeshClean Debugger..."
        echo ""
        python start_ui.py
        ;;
        
    2)
        echo ""
        print_step "Building Docker image..."
        
        if ! command -v docker &> /dev/null; then
            print_warning "Docker not found. Please install Docker Desktop"
            exit 1
        fi
        
        print_step "Building: meshclean-debugger:latest"
        docker build -t meshclean-debugger:latest .
        print_success "Docker image built"
        
        echo ""
        print_step "Running Docker container..."
        docker run -p 7860:7860 meshclean-debugger:latest
        ;;
        
    3)
        echo ""
        print_step "Verifying all components..."
        
        # Python imports
        print_step "Testing Python imports..."
        python3 -c "from pipeline_debug_env import PipelineDebugEnv; print('✓ Core imports OK')"
        print_success "Core imports verified"
        
        # Inference
        python3 -c "from inference import DebugAgent; print('✓ Agent imports OK')"
        print_success "Agent imports verified"
        
        # Requirements
        print_step "Checking requirements..."
        if [ -f "requirements.txt" ]; then
            print_success "requirements.txt found"
            head -5 requirements.txt | sed 's/^/  /'
            echo "  ..."
        fi
        
        # Dockerfile
        print_step "Checking Dockerfile..."
        if [ -f "Dockerfile" ]; then
            print_success "Dockerfile found"
            grep -E "^FROM|^EXPOSE|^CMD" Dockerfile | sed 's/^/  /'
        fi
        
        echo ""
        print_success "All components verified!"
        ;;
        
    4)
        echo ""
        print_step "Initializing GitHub repository..."
        
        if ! command -v git &> /dev/null; then
            print_warning "Git not found. Please install Git"
            exit 1
        fi
        
        if [ ! -d ".git" ]; then
            print_step "Initializing git..."
            git init
            print_success "Git initialized"
        fi
        
        print_step "Adding files..."
        git add -A
        
        print_step "Creating initial commit..."
        git commit -m "Initial commit: MeshClean Debugger" || echo "Already committed"
        print_success "Repository ready"
        
        echo ""
        echo "Next steps:"
        echo "1. Create repository on GitHub: https://github.com/new"
        echo "2. Run these commands:"
        echo "   git remote add origin https://github.com/YOUR_USERNAME/meshclean-debugger.git"
        echo "   git branch -M main"
        echo "   git push -u origin main"
        ;;
        
    5)
        echo ""
        print_step "Testing all tasks..."
        
        python3 << 'EOF'
from inference import DebugAgent

tasks = ['task_1', 'task_2', 'task_3']
results = []

for task_id in tasks:
    try:
        agent = DebugAgent(task_id)
        result = agent.run()
        grade = result.get('grade', 0.0)
        results.append((task_id, 'PASS', f"{grade:.1%}"))
    except Exception as e:
        results.append((task_id, 'FAIL', str(e)))

print("\nTest Results:")
print("-" * 50)
for task_id, status, detail in results:
    print(f"  {task_id:15} {status:6} {detail}")
print("-" * 50)
print()
EOF
        ;;
        
    *)
        print_warning "Invalid option"
        exit 1
        ;;
esac

echo ""
print_success "Done!"
