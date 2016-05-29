from flask import Blueprint, render_template, flash, redirect, url_for
from flask_babel import gettext
from flask_login import login_required, current_user

from web.forms import CategoryForm
from web.lib.utils import redirect_url
from web.lib.view_utils import etag_match
from web.controllers import ArticleController, FeedController, \
                            CategoryController

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')
category_bp = Blueprint('category', __name__, url_prefix='/category')


@categories_bp.route('/', methods=['GET'])
@login_required
@etag_match
def list_():
    "Lists the subscribed  feeds in a table."
    art_contr = ArticleController(current_user.id)
    return render_template('categories.html',
            categories=list(CategoryController(current_user.id).read().order_by('name')),
            feeds_count=FeedController(current_user.id).count_by_category(),
            unread_article_count=art_contr.count_by_category(readed=False),
            article_count=art_contr.count_by_category())


@category_bp.route('/create', methods=['GET'])
@category_bp.route('/edit/<int:category_id>', methods=['GET'])
@login_required
@etag_match
def form(category_id=None):
    action = gettext("Add a category")
    head_titles = [action]
    if category_id is None:
        return render_template('edit_category.html', action=action,
                               head_titles=head_titles, form=CategoryForm())
    category = CategoryController(current_user.id).get(id=category_id)
    action = gettext('Edit category')
    head_titles = [action]
    if category.name:
        head_titles.append(category.name)
    return render_template('edit_category.html', action=action,
                           head_titles=head_titles, category=category,
                           form=CategoryForm(obj=category))


@category_bp.route('/delete/<int:category_id>', methods=['GET'])
@login_required
def delete(category_id=None):
    category = CategoryController(current_user.id).delete(category_id)
    flash(gettext("Category %(category_name)s successfully deleted.",
                  category_name=category.name), 'success')
    return redirect(redirect_url())


@category_bp.route('/create', methods=['POST'])
@category_bp.route('/edit/<int:category_id>', methods=['POST'])
@login_required
def process_form(category_id=None):
    form = CategoryForm()
    cat_contr = CategoryController(current_user.id)

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
