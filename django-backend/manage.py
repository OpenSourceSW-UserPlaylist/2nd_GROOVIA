#!/usr/bin/env python
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotify_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()

# https version
'''
if __name__ == "__main__":
    import sys
    from django.core.management import execute_from_command_line

    # runserver 명령을 runserver_plus + HTTPS 인증서로 자동 변환
    if len(sys.argv) > 1 and sys.argv[1] == "runserver":
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotify_project.settings')  # 환경 변수 보장
        sys.argv[1] = "runserver_plus"
        sys.argv += [
            "--cert-file", "localhost-cert.pem",
            "--key-file", "localhost-key.pem"
        ]
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotify_project.settings')

    execute_from_command_line(sys.argv)
'''