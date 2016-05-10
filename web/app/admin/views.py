from flask import (current_app,
                   flash,
                   redirect,
                   render_template,
                   request,
                   url_for,
                   jsonify,
                   abort)

from flask_login import (login_user,
                         logout_user,
                         login_required,
                         current_user)

from . import admin
from .. import db
from ..decorators import admin_required, permission_required
from .forms import (AddTeacherForm,
                    ExcelUploadForm,
                    EditTeacherForm,
                    AddWorkPeriodForm,
                    EditWorkPeriodForm)
from ..models import User, WorkPeriod
from sqlalchemy import desc
from werkzeug import secure_filename
import openpyxl
import re
#TODO Add openpyxl to requirements.txt


@admin.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def index():
    """Main route for admin user interface.

    Administrator permissions is required to
    grant acess to this page.
    """
    return render_template('admin/admin.html')


@admin.route('/teachers')
@login_required
@admin_required
def teachers():
    teachers = User.query.filter_by(password_hash=None, is_active=True).order_by(User.first_name)
    return render_template('admin/teachers.html', teachers=teachers)


@admin.route('/teachers/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_teacher():
    form = AddTeacherForm()

    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.teachers'))

    return render_template('admin/add.html',
                           form=form,
                           form_name='lärare',
                           previous_page_url=url_for('admin.teachers'))


@admin.route('/teachers/remove', methods=['POST'])
@login_required
@admin_required
def remove_teacher():
    data = request.get_json()

    if data:
        id = data['user']
        user = User.query.filter_by(id=id).first()

        if user:
            user.is_active = False
            db.session.commit()
        else:
            abort(400)

    return ''


@admin.route('/teachers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_teacher(id):
    user = User.query.filter_by(id=id).first()

    if user:
        form = EditTeacherForm(obj=user)

        if form.validate_on_submit():
            form.populate_obj(user)
            db.session.commit()
            return redirect(url_for('admin.teachers'))

        return render_template('admin/edit.html',
                               form=form,
                               form_name='lärare',
                               previous_page_url=url_for('admin.teachers'))

    else:
        abort(400)


@admin.route('/teachers/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_teachers():
    form = ExcelUploadForm()

    if form.validate_on_submit():
        filename = secure_filename(form.file.data.filename)
        file = form.file.data
        if file:            
            wb = openpyxl.load_workbook(file)

            for sheet in wb.worksheets:
                for row in range(1, sheet.max_row + 1):
                    first_name = sheet['A' + str(row)].value
                    last_name = sheet['B' + str(row)].value
                    email = sheet['C' + str(row)].value
                    work_hours = sheet['D' + str(row)].value
 
                    # TODO - Change flashed messages for if statements.
                    if first_name is None or last_name is None or email is None or work_hours is None:
                        continue

                    if re.match('^[A-Ö]*(-| )?[A-Ö]*(-| )?[A-Ö]*$', first_name) == False:
                        flash('Kunde inte lägga till {first_name} {last_name}, eftersom {first_name} inte är ett godkänt förnamn.'.format(first_name=first_name, last_name=last_name))
                        continue

                    if re.match('^[A-Ö]*(-| )?[A-Ö]*(-| )?[A-Ö]*$', last_name) == False:
                        flash('Kunde inte lägga till {first_name} {last_name}, eftersom {last_name} inte är ett godkänt efternamn.'.format(first_name=first_name, last_name=last_name))
                        continue

                    if re.match('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email) == False:
                        flash('Kunde inte lägga till {first_name} {last_name}, eftersom {email} inte är en godkänd e-postadress.'.format(first_name=first_name, last_name=last_name, email=email))
                        continue

                    if type(work_hours) != int:
                        flash('Kunde inte lägga till {first_name} {last_name}, eftersom {work_hours} inte är en siffra.'.format(first_name=first_name, last_name=last_name, work_hours=work_hours))

                    existing_user = User.query.filter_by(email=email).first()
                    if existing_user:
                        flash('{} är redan inlagd i systemet.'.format(email))
                        continue
                    else:
                        user = User(first_name=first_name, last_name=last_name, email=email)
                        db.session.add(user)

            db.session.commit()

        return redirect(url_for('admin.teachers'))
    return render_template('admin/upload.html', form=form)


@admin.route('/work-periods/', methods=['GET', 'POST'])
@login_required
@admin_required
def work_periods():
    work_periods = WorkPeriod.query.order_by(desc(WorkPeriod.start))
    # TODO - fix date-datatype and populate db
    return render_template('admin/work_periods.html', work_periods=work_periods)


@admin.route('/work-periods/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_work_period():
    form = AddWorkPeriodForm()

    if form.validate_on_submit():
        work_period = WorkPeriod(start=form.start.data, end=form.end.data)
        db.session.add(work_period)
        db.session.commit()
        return redirect(url_for('admin.work_periods'))

    return render_template('admin/add.html',
                           form=form,
                           form_name='arbetsperiod',
                           previous_page_url=url_for('admin.work_periods'))


@admin.route('/work-periods/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_work_period(id):
    work_period = WorkPeriod.query.filter_by(id=id).first()

    if work_period:
        form = EditWorkPeriodForm(obj=work_period)

        if form.validate_on_submit():
            form.populate_obj(work_period)
            db.session.commit()
            return redirect(url_for('admin.work_periods'))

        return render_template('admin/edit.html',
                               form=form,
                               form_name='arbetsperiod',
                               previous_page_url=url_for('admin.work_periods'))

    else:
        abort(400)
