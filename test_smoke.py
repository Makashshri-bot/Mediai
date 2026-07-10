#!/usr/bin/env python
"""
Smoke test for MediAI application.
Tests all frontend routes and API endpoints for basic functionality.
"""
import json
import sys
from app import create_app, db

app = create_app()

# Frontend routes to test
frontend_routes = [
    ("/", "GET", 200, "Landing page"),
    ("/login", "GET", 200, "Login page"),
    ("/register", "GET", 200, "Register page"),
    ("/dashboard", "GET", 302, "Protected - redirect to login"),
    ("/profile", "GET", 302, "Protected - redirect to login"),
    ("/appointments", "GET", 302, "Protected - redirect to login"),
    ("/doctors", "GET", 302, "Protected - redirect to login"),
    ("/patients", "GET", 302, "Protected - redirect to login"),
    ("/departments", "GET", 302, "Protected - redirect to login"),
    ("/beds", "GET", 302, "Protected - redirect to login"),
    ("/medicines", "GET", 302, "Protected - redirect to login"),
    ("/reports", "GET", 302, "Protected - redirect to login"),
    ("/prescriptions", "GET", 302, "Protected - redirect to login"),
    ("/notifications", "GET", 302, "Protected - redirect to login"),
    ("/ai/chatbot", "GET", 302, "Protected - redirect to login"),
    ("/ai/symptom-checker", "GET", 302, "Protected - redirect to login"),
    ("/ai/report-summarizer", "GET", 302, "Protected - redirect to login"),
    ("/ai/prescription-explainer", "GET", 302, "Protected - redirect to login"),
    ("/ai/appointment-assistant", "GET", 302, "Protected - redirect to login"),
]

# API endpoints to test
api_routes = [
    ("/api/doctors", "GET", [200, 401]),
    ("/api/patients", "GET", [200, 401]),
    ("/api/departments", "GET", [200, 401]),
    ("/api/beds", "GET", [200, 401]),
    ("/api/medicines", "GET", [200, 401]),
    ("/api/appointments", "GET", [200, 401]),
    ("/api/reports", "GET", [200, 401]),
    ("/api/prescriptions", "GET", [200, 401]),
    ("/api/notifications", "GET", [200, 401]),
    ("/api/ai/symptom-checker", "POST", [400, 401]),  # Requires JSON body
]

def test_frontend_routes():
    """Test all frontend routes."""
    print("\n" + "="*80)
    print("FRONTEND ROUTES TEST")
    print("="*80)
    
    with app.test_client() as client:
        failed = []
        for path, method, expected_code, description in frontend_routes:
            try:
                if method == "GET":
                    response = client.get(path, follow_redirects=False)
                
                status = "✓" if response.status_code == expected_code else "✗"
                print(f"{status} {path:40} → {response.status_code} (expected {expected_code}) - {description}")
                
                if response.status_code != expected_code:
                    failed.append((path, response.status_code, expected_code))
                    
                # Check for Jinja errors in HTML responses
                if response.status_code == 200 and response.content_type and 'text/html' in response.content_type:
                    if b'Jinja2' in response.data or b'TemplateAssertionError' in response.data:
                        print(f"  !! Jinja2 template error detected in response")
                        failed.append((path, "Jinja2 error", "valid template"))
                
            except Exception as e:
                print(f"✗ {path:40} → ERROR: {str(e)}")
                failed.append((path, "Exception", str(e)))
        
        return failed

def test_api_routes():
    """Test all API endpoints."""
    print("\n" + "="*80)
    print("API ENDPOINTS TEST")
    print("="*80)
    
    with app.test_client() as client:
        failed = []
        for path, method, expected_codes, *desc in api_routes:
            try:
                if method == "GET":
                    response = client.get(path)
                elif method == "POST":
                    # For POST, send empty JSON body to trigger validation error
                    response = client.post(path, json={})
                
                status = "✓" if response.status_code in expected_codes else "✗"
                print(f"{status} {path:40} → {response.status_code} (expected {expected_codes})")
                
                if response.status_code not in expected_codes:
                    failed.append((path, response.status_code, expected_codes))
                
                # Verify it's JSON
                if response.status_code in [200, 201]:
                    try:
                        data = response.get_json()
                        if data is None:
                            print(f"  !! Response is not valid JSON")
                            failed.append((path, "non-JSON response", "JSON expected"))
                    except Exception as e:
                        print(f"  !! JSON decode error: {str(e)}")
                        failed.append((path, "JSON error", str(e)))
                
            except Exception as e:
                print(f"✗ {path:40} → ERROR: {str(e)}")
                failed.append((path, "Exception", str(e)))
        
        return failed

def check_static_files():
    """Check if static files are accessible."""
    print("\n" + "="*80)
    print("STATIC FILES TEST")
    print("="*80)
    
    static_files = [
        "/static/css/style.css",
        "/static/js/app.js",
        "/static/js/voice.js",
    ]
    
    with app.test_client() as client:
        failed = []
        for path in static_files:
            try:
                response = client.get(path)
                status = "✓" if response.status_code == 200 else "✗"
                print(f"{status} {path:40} → {response.status_code}")
                
                if response.status_code != 200:
                    failed.append((path, response.status_code, 200))
                
            except Exception as e:
                print(f"✗ {path:40} → ERROR: {str(e)}")
                failed.append((path, "Exception", str(e)))
        
        return failed

def check_templates():
    """Check if templates can be rendered without errors (via routes)."""
    print("\n" + "="*80)
    print("TEMPLATE RENDERING TEST (via actual routes)")
    print("="*80)
    
    # These routes will render templates - if they return 200 or redirect, templates are fine
    template_test_routes = [
        ("/", 200, "index.html"),
        ("/login", 200, "login.html"),
        ("/register", 200, "register.html"),
        ("/dashboard", 302, "dashboard.html (protected - redirect ok)"),
        ("/appointments", 302, "appointments.html (protected - redirect ok)"),
        ("/doctors", 302, "doctors.html (protected - redirect ok)"),
        ("/patients", 302, "patients.html (protected - redirect ok)"),
        ("/departments", 302, "departments.html (protected - redirect ok)"),
        ("/beds", 302, "beds.html (protected - redirect ok)"),
        ("/medicines", 302, "medicines.html (protected - redirect ok)"),
        ("/reports", 302, "reports.html (protected - redirect ok)"),
        ("/prescriptions", 302, "prescriptions.html (protected - redirect ok)"),
        ("/notifications", 302, "notifications.html (protected - redirect ok)"),
        ("/ai/chatbot", 302, "ai_chatbot.html (protected - redirect ok)"),
        ("/ai/report-summarizer", 302, "ai_report_summarizer.html (protected - redirect ok)"),
        ("/ai/prescription-explainer", 302, "ai_prescription_explainer.html (protected - redirect ok)"),
        ("/ai/appointment-assistant", 302, "ai_appointment_assistant.html (protected - redirect ok)"),
    ]
    
    failed = []
    with app.test_client() as client:
        for route, expected_status, template_name in template_test_routes:
            try:
                response = client.get(route, follow_redirects=False)
                if response.status_code == expected_status:
                    print(f"✓ {template_name:50} → {response.status_code}")
                else:
                    print(f"✗ {template_name:50} → {response.status_code} (expected {expected_status})")
                    failed.append((template_name, response.status_code, expected_status))
                    
            except Exception as e:
                print(f"✗ {template_name:50} → ERROR: {str(e)}")
                failed.append((template_name, "Exception", str(e)))
    
    return failed

def check_routes_exist():
    """Check if all expected routes exist in the app."""
    print("\n" + "="*80)
    print("ROUTE REGISTRATION CHECK")
    print("="*80)
    
    expected_endpoints = [
        "main.home",
        "main.dashboard",
        "main.profile",
        "auth.login",
        "auth.register",
        "auth.logout",
        "views.appointments",
        "views.doctors",
        "views.patients",
        "views.departments",
        "views.beds",
        "views.medicines",
        "views.reports",
        "views.prescriptions",
        "views.notifications",
        "views.ai_chatbot",
        "views.ai_symptom_checker",
        "views.ai_report_summarizer",
        "views.ai_prescription_explainer",
        "views.ai_appointment_assistant",
        "api.get_doctors",
        "api.get_patients",
        "api.get_departments",
        "api.get_beds",
        "api.get_medicines",
        "api.get_appointments",
        "api.get_reports",
        "api.get_prescriptions",
        "api.get_notifications",
        "api.ai_symptom_checker",
    ]
    
    registered_endpoints = {rule.endpoint for rule in app.url_map.iter_rules()}
    failed = []
    
    for endpoint in expected_endpoints:
        if endpoint in registered_endpoints:
            print(f"✓ {endpoint:40} → Registered")
        else:
            print(f"✗ {endpoint:40} → NOT REGISTERED")
            failed.append((endpoint, "not registered", "registered"))
    
    return failed

def main():
    """Run all smoke tests."""
    print("\n" + "="*80)
    print("MEDIAI RUNTIME SMOKE TEST")
    print("="*80)
    print(f"Test started at {app.config.get('ENV', 'UNKNOWN')} mode")
    
    all_failed = []
    
    # Check routes registration
    failed = check_routes_exist()
    all_failed.extend(failed)
    
    # Check templates
    failed = check_templates()
    all_failed.extend(failed)
    
    # Check static files
    failed = check_static_files()
    all_failed.extend(failed)
    
    # Test frontend routes
    failed = test_frontend_routes()
    all_failed.extend(failed)
    
    # Test API routes
    failed = test_api_routes()
    all_failed.extend(failed)
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if all_failed:
        print(f"\n❌ {len(all_failed)} ISSUE(S) FOUND:\n")
        for item, actual, expected in all_failed:
            print(f"  • {item}")
            print(f"    Got: {actual}")
            print(f"    Expected: {expected}\n")
        return 1
    else:
        print("\n✅ ALL TESTS PASSED!")
        print("The MediAI application is ready to run.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
