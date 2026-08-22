from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.employee import Employee

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/employees')
@login_required
def employee_list():
    employees = Employee.query.order_by(Employee.id.desc()).all()
    total_payroll = sum(e.salary for e in employees if e.status == 'Active')
    active_count = sum(1 for e in employees if e.status == 'Active')

    return render_template(
        'employees.html',
        employees=employees,
        total_payroll=round(total_payroll, 2),
        active_count=active_count,
        today=date.today().strftime('%Y-%m-%d')
    )

@employee_bp.route('/employees/add', methods=['POST'])
@login_required
def add_employee():
    name = request.form.get('name', '').strip()
    role = request.form.get('role', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    salary = request.form.get('salary', '0')
    joining_date_str = request.form.get('joining_date', '')
    status = request.form.get('status', 'Active')
    address = request.form.get('address', '').strip()

    if not name or not role or not phone:
        flash('Name, Role, and Phone are required.', 'danger')
        return redirect(url_for('employee.employee_list'))

    try:
        joining_date = datetime.strptime(joining_date_str, '%Y-%m-%d').date() if joining_date_str else date.today()
        sal_val = float(salary) if salary else 0.0

        emp = Employee(
            name=name,
            role=role,
            phone=phone,
            email=email if email else None,
            salary=sal_val,
            joining_date=joining_date,
            status=status,
            address=address
        )
        db.session.add(emp)
        db.session.commit()
        flash(f'Employee "{name}" added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding employee: {str(e)}', 'danger')

    return redirect(url_for('employee.employee_list'))

@employee_bp.route('/employees/edit/<int:id>', methods=['POST'])
@login_required
def edit_employee(id):
    emp = Employee.query.get_or_404(id)
    emp.name = request.form.get('name', emp.name).strip()
    emp.role = request.form.get('role', emp.role).strip()
    emp.phone = request.form.get('phone', emp.phone).strip()
    emp.email = request.form.get('email', emp.email).strip() or None
    salary_str = request.form.get('salary')
    if salary_str:
        emp.salary = float(salary_str)
    emp.status = request.form.get('status', emp.status)
    emp.address = request.form.get('address', emp.address).strip()

    db.session.commit()
    flash(f'Employee {emp.name} updated.', 'success')
    return redirect(url_for('employee.employee_list'))

@employee_bp.route('/employees/delete/<int:id>', methods=['POST'])
@login_required
def delete_employee(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    flash(f'Employee record deleted.', 'info')
    return redirect(url_for('employee.employee_list'))
