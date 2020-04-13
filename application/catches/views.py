from flask import redirect, render_template, request, url_for
from flask_login import current_user

from application import app, db, login_required
from application.catches.models import Catch
from application.catches.forms import CatchForm
from application.auth.models import User
from application.fish.models import Fish

@app.route("/catches", methods=["GET"])
def catches_index():
    return render_template("catches/list.html", catches = Catch.query.all())

@app.route("/catches/new/")
@login_required(role="USER")
def catches_form():
    return render_template("catches/new.html", form = CatchForm())

@app.route("/catches/", methods=["POST"])
@login_required(role="USER")
def catches_create():
    form = CatchForm(request.form)

    if not form.validate():
        return render_template("catches/new.html", form = form)

    #Find the species from fish table.
    s_id = Fish.find_id_based_on_name(name= form.species.data.lower().strip())
    if s_id == None:
        return render_template("catches/new.html", form = form,
                               error = "No such a species!")
    c = Catch(
              form.lure_or_fly.data,
              form.length.data,
              form.weight.data,
              form.spot.data.capitalize(),
              form.description.data,
              form.private_or_public.data)
    c.species_id = s_id
    c.account_id = current_user.id
    c.fisher = current_user.name
    db.session().add(c)
    db.session().commit()

    return redirect(url_for("catches_index"))
#Variable used to store the id of the catch in the processing. 
catchId = 0

@app.route("/catches/<catch_id>/", methods=["POST"])
@login_required
def catches_change_or_delete(catch_id):

    global catchId
    catchId = catch_id
    catch = Catch.query.get(catch_id)
    #Check that catch is user's own catch or current user has admin/owner role.
    if catch.account_id != current_user.id and current_user.role < 2:
        return loqin_manager.unauthorized()

    form = CatchForm()
    #To show old choices in a form, set SelectField values correct.
    if catch.lure_or_fly == 'fly':
        form.change_choice('fly')
    else:
        form.change_choice('lure')
    if catch.private_or_public == 'public':
        form.change_privacy('public')
    else:
        form.change_privacy('private')
    return render_template("catches/change_or_delete.html", form = form, catch = catch)

@app.route("/catches/catchId", methods=["POST"])
@login_required
def catches_save():

    form = CatchForm(request.form)
    c = Catch.query.get(catchId)

    if catch.account_id != current_user.id and current_user.role < 2:
        return loqin_manager.unauthorized()

    if form.delete.data:
        db.session().delete(c)
        db.session().commit()

        return redirect(url_for("catches_index"))

    if not form.validate():
        return render_template("catches/change_or_delete.html", form = form, catch = c)

    c.species = form.species.data.lower().strip()
    c.lure_or_fly = form.lure_or_fly.data
    c.length = form.length.data
    c.weight = form.weight.data
    c.spot = form.spot.data.capitalize()
    c.description = form.description.data
    c.private_or_public = form.private_or_public.data
    c.account_id = current_user.id
    c.fisher = current_user.name
    db.session().commit()

    return redirect(url_for("catches_index"))

