# 🌐 ntkrv.dev — Personal Portfolio by Nicolas Tokariev

> A modern, responsive portfolio website built with **Flask** and **Tailwind CSS**, showcasing my work in **Data Analytics**, **Software Engineering**, and **DevOps Automation**.

---

## 🧩 Overview

**ntkrv.dev** is a personal portfolio designed to present my professional background, technical skills, and selected projects in a clean and interactive way.  
The site demonstrates both **backend and frontend engineering** skills, combining Flask modular architecture with a modern Tailwind-powered user interface.

---

## 🚀 Key Features

- ⚡ **Dynamic Projects Showcase** — portfolio projects are managed and displayed dynamically.  
- 🧠 **Certificates Section** — verified professional achievements with detailed skill tags.  
- 💬 **Contact Form** — allows visitors to send messages securely.  
- 🌗 **Dark / Light Mode** — theme automatically adapts to the system settings.  
- 🧩 **Modular Architecture** — Flask Blueprints for scalable and maintainable structure.  
- 🎨 **Tailwind CSS UI** — modern, responsive, and minimalist frontend design.  
- 🔒 **Secure Routing & Forms** — input validation and protection against common web attacks.  
- ⚙️ **Automation Support** — includes PowerShell tools for automated linting, migration, and CSS build.  
- 🌍 **SEO-Optimized** — metadata and structure designed for discoverability and indexing.  

---

## 🧠 Tech Stack

| Layer | Technologies |
|--------|---------------|
| **Framework** | Flask (Python) |
| **Frontend** | Tailwind CSS, HTML5, JavaScript |
| **Architecture** | Flask Blueprints, Jinja2 Templates |
| **Automation & Tools** | Git, PowerShell, npm, Black, Flake8 |

---
## 🧠 Core Functionality

### 🖥️ Portfolio Homepage
- Introduction and summary of technical background.  
- Highlights core skills and technologies with categorized tags.  
- Displays featured projects with images, short descriptions, and links.  

### 🧾 Projects Section
- Displays detailed project information dynamically.  
- Each project includes title, stack, description, and external link (GitHub, report, etc.).  
- All projects are stored in a structured and extendable format.

### 🏅 Certificates Section
- Lists certifications with issuing organizations and relevant technical skills.  
- Each certificate includes a secure external verification link.  
- Optimized for responsive design and accessibility.

### 📬 Contact Section
- Allows visitors to send inquiries directly from the site.  
- Built with CSRF protection and secure mail integration.  
- Validates all form inputs before sending.

### 🧰 Admin Functionality
- Enables content management (projects and certificates).  
- Protected routes and server-side validation ensure secure operation.  
- Follows Flask’s best practices for session and authentication handling.

---

## ⚙️ Development Workflow

The project includes a PowerShell automation script (`run_dev.ps1`) to streamline the development process:

- Installs dependencies  
- Runs code formatters (`black`) and linters (`flake8`)  
- Applies database migrations  
- Builds Tailwind CSS  
- Starts the Flask server  
