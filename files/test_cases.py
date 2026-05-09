"""
Evaluation dataset: 10 real product prompts + 10 edge cases
"""

REAL_PROMPTS = [
    {
        "id": "R01",
        "category": "CRM",
        "prompt": "Build a CRM with login, contacts management, deal pipeline, dashboard with analytics, role-based access for admin and sales reps, and premium plan with Stripe payments. Admins can see all analytics."
    },
    {
        "id": "R02",
        "category": "E-commerce",
        "prompt": "Create an e-commerce platform with product catalog, shopping cart, checkout with payments, order tracking, admin panel for inventory, and customer accounts."
    },
    {
        "id": "R03",
        "category": "Project Management",
        "prompt": "Build a project management tool like Trello with boards, lists, cards, team collaboration, due dates, file attachments, and notifications."
    },
    {
        "id": "R04",
        "category": "Healthcare",
        "prompt": "Create a clinic management system with patient records, appointment booking, doctor schedules, billing, prescription management, and admin reports."
    },
    {
        "id": "R05",
        "category": "LMS",
        "prompt": "Build a learning management system with course creation, video lessons, quizzes, student progress tracking, certificates, instructor dashboard, and subscription payments."
    },
    {
        "id": "R06",
        "category": "HR",
        "prompt": "Create an HR management platform with employee onboarding, leave management, payroll, performance reviews, org chart, and role-based access for HR managers and employees."
    },
    {
        "id": "R07",
        "category": "Real Estate",
        "prompt": "Build a real estate listing platform where agents can post properties, buyers can search and filter, schedule viewings, and an admin manages listings and agents."
    },
    {
        "id": "R08",
        "category": "Food Delivery",
        "prompt": "Create a food delivery app with restaurant listings, menu management, cart, real-time order tracking, delivery agent assignment, ratings, and payments."
    },
    {
        "id": "R09",
        "category": "SaaS Analytics",
        "prompt": "Build a SaaS analytics dashboard where users connect data sources, create charts, build dashboards, set alerts, and share reports. Team plans with seat-based billing."
    },
    {
        "id": "R10",
        "category": "Social Platform",
        "prompt": "Create a professional networking platform with user profiles, connections, posts, messaging, job listings, company pages, and premium subscription for advanced features."
    }
]

EDGE_CASES = [
    {
        "id": "E01",
        "category": "vague",
        "prompt": "Build an app for my business",
        "expected_behavior": "Should ask for clarification or make broad assumptions and document them"
    },
    {
        "id": "E02",
        "category": "vague",
        "prompt": "I need a website with users",
        "expected_behavior": "Should infer minimal viable app and document assumptions"
    },
    {
        "id": "E03",
        "category": "conflicting",
        "prompt": "Build an app where all users are admins but admins have special access that users don't have",
        "expected_behavior": "Should detect conflict and resolve with a clear role hierarchy"
    },
    {
        "id": "E04",
        "category": "conflicting",
        "prompt": "Make everything free but also charge users for everything",
        "expected_behavior": "Should detect business logic conflict and ask for clarification or implement freemium"
    },
    {
        "id": "E05",
        "category": "incomplete",
        "prompt": "Build a marketplace",
        "expected_behavior": "Should infer buyer/seller roles, listings, transactions and document all assumptions"
    },
    {
        "id": "E06",
        "category": "incomplete",
        "prompt": "Create a dashboard",
        "expected_behavior": "Should ask what data to show or make generic analytics dashboard"
    },
    {
        "id": "E07",
        "category": "overspecified",
        "prompt": "Build a todo app with login, teams, projects, sub-projects, sub-tasks, comments, attachments, time tracking, invoicing, CRM, email marketing, and AI assistant",
        "expected_behavior": "Should handle complexity and generate all layers correctly"
    },
    {
        "id": "E08",
        "category": "ambiguous_roles",
        "prompt": "Build a platform where doctors and patients interact but also pharmacies and insurance companies",
        "expected_behavior": "Should correctly model 4 distinct roles with appropriate permissions"
    },
    {
        "id": "E09",
        "category": "no_auth",
        "prompt": "Create a simple public blog with posts and comments, no login needed",
        "expected_behavior": "Should generate schema with auth_required=false, public routes"
    },
    {
        "id": "E10",
        "category": "single_feature",
        "prompt": "Just a contact form that emails me",
        "expected_behavior": "Should generate minimal schema, not over-engineer it"
    }
]

ALL_TEST_CASES = REAL_PROMPTS + EDGE_CASES
