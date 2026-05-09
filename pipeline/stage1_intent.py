import re
import os

def extract_intent(user_input: str) -> dict:
    words = user_input.lower()
    entities = []
    for kw, entity in [("user", "User"), ("contact", "Contact"), ("product", "Product"),
                        ("order", "Order"), ("invoice", "Invoice"), ("task", "Task"),
                        ("project", "Project"), ("employee", "Employee"), ("customer", "Customer"),
                        ("patient", "Patient"), ("doctor", "Doctor"), ("student", "Student")]:
        if kw in words:
            entities.append(entity)
    if not entities:
        entities = ["User", "Item"]

    roles = ["admin", "user"]
    for kw, role in [("sales", "sales_rep"), ("manager", "manager"),
                     ("doctor", "doctor"), ("patient", "patient"), ("agent", "agent"),
                     ("teacher", "teacher"), ("student", "student")]:
        if kw in words:
            roles.append(role)

    features = []
    for f in ["login", "dashboard", "payments", "analytics", "contacts",
              "reports", "notifications", "search", "chat", "calendar", "billing"]:
        if f in words:
            features.append(f)
    if not features:
        features = ["login", "dashboard"]

    app_type = "Web Application"
    for kw, t in [("crm", "CRM"), ("ecommerce", "E-commerce"), ("store", "E-commerce"),
                  ("shop", "E-commerce"), ("blog", "Blog"), ("lms", "LMS"),
                  ("course", "LMS"), ("hr", "HR Management"), ("clinic", "Healthcare")]:
        if kw in words:
            app_type = t
            break

    app_name = user_input.split()[0].title() if user_input.split() else "App"

    result = {
        "app_name": app_name,
        "app_type": app_type,
        "entities": entities,
        "features": features,
        "roles": roles,
        "auth_required": any(w in words for w in ["login", "auth", "sign", "register", "password"]),
        "payment_required": any(w in words for w in ["payment", "stripe", "pay", "billing", "subscription"]),
        "ambiguities": [],
        "assumptions": ["Entities and features inferred from description keywords"]
    }
    result["_meta"] = {"stage": "intent_extraction", "input_tokens": 0, "output_tokens": 0}
    return result
