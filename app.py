import os
import sys
import runpy

project_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'DairyFarmQR-main')
inner_app = os.path.join(project_dir, 'app.py')

if __name__ == '__main__':
    if os.path.exists(project_dir):
        os.chdir(project_dir)
        if project_dir not in sys.path:
            sys.path.insert(0, project_dir)
    runpy.run_path(inner_app, run_name='__main__')
