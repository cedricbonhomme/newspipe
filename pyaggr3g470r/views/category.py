from flask import g, Blueprint, render_template, flash, redirect, url_for
from flask.ext.babel import gettext
from flask.ext.login import login_required

from pyaggr3g470r.forms import AddCategoryForm
from pyaggr3g470r.lib.view_utils import etag_match
from pyaggr3g470r.controllers.category import CategoryController

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')
category_bp = Blueprint('category', __name__, url_prefix='/category')


@category_bp.route('/create', methods=['GET'])
@category_bp.route('/edit/<int:category_id>', methods=['GET'])
@login_required
@etag_match
def form(category_id=None):
    action = gettext("Add a category")
    head_titles = [action]
    if category_id is None:
        return render_template('edit_category.html', action=action,
                               head_titles=head_titles, form=AddCategoryForm())
    category = CategoryController(g.user.id).get(id=category_id)
    action = gettext('Edit category')
    head_titles = [action]
    if category.name:
        head_titles.append(category.name)
    return render_template('edit_category.html', action=action,
                           head_titles=head_titles, category=category,
                           form=AddCategoryForm(obj=category))


@category_bp.route('/create', methods=['POST'])
@category_bp.route('/edit/<int:cat_id>', methods=['POST'])
@login_required
def process_form(category_id=None):
    form = AddCategoryForm()
    cat_contr = CategoryController(g.user.id)

    if not form.validate():
        return render_template('edit_category.html', form=form)
    existing_cats = list(cat_contr.read(name=form.name.data))
    if existing_cats and category_id is None:
        flash(gettext("Couldn't add category: already exists."), "warning")
        return redirect(url_for('category.form',
                                category_id=existing_cats[0].id))
    # Edit an existing category
    category_attr = {'name': form.name.data}

    if category_id is not None:
        cat_contr.update({'id': category_id}, category_attr)
        flash(gettext('Category %(cat_name)r successfully updated.',
                      cat_name=category_attr['name']), 'success')
        return redirect(url_for('category.form', category_id=category_id))

    # Create a new category
    new_category = cat_contr.create(**category_attr)

    flash(gettext('Category %(category_name)r successfully created.',
                  category_name=new_category.name), 'success')

    return redirect(url_for('category.form', category_id=new_category.id))
