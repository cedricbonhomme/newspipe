/*!
* Newspipe - A web news aggregator.
* Copyright (C) 2010-2026 Cédric Bonhomme - https://www.cedricbonhomme.org
*
* For more information: https://github.com/cedricbonhomme/newspipe
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU Affero General Public License as
* published by the Free Software Foundation, either version 3 of the
* License, or (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU Affero General Public License for more details.
*
* You should have received a copy of the GNU Affero General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

function change_unread_counter(feed_id, increment) {
    el = document.getElementById("unread-"+feed_id)
    if (el != null) {
      var new_value = parseInt(el.textContent) + increment;
      document.getElementById("unread-"+feed_id).textContent = new_value;
    }

    document.getElementById("total-unread").textContent = parseInt(document.getElementById("total-unread").textContent) + increment;

    if (new_value == 0) {
        document.getElementById("unread-"+feed_id).display = "none";
    }
}


// Mark an article as read when it is opened in a new tab
document.querySelectorAll(".open-article").forEach(el => {
  el.addEventListener("click", function() {
    const feedContainer = this.closest("[data-bs-feed]");
    if (!feedContainer) return;

    const feed_id = feedContainer.dataset.bsFeed;
    if (!/^[0-9a-fA-F-]+$/.test(feed_id)) return;
    const filterEl = document.getElementById("filters");
    const filter = filterEl ? filterEl.dataset.filter : null;

    if (filter === "unread") {
      feedContainer.remove();
      change_unread_counter(feed_id, -1);
    }
  });
});


// True when the current view is the "read later" one; its articles are not
// counted in the unread badges.
function is_read_later_view() {
    var filters = document.getElementById("filters");
    return filters != null && filters.getAttribute("data-read-later") == "1";
}


// Mark an article as read or unread from the home page (event-delegated so it
// also works for rows added by infinite scroll).
document.addEventListener("click", function(event) {
    var node = event.target.closest(".readed");
    if (!node) return;
    var row = node.closest("[data-article]");
    if (!row) return;
    var article_id = row.getAttribute("data-article");
    var feed_id = row.getAttribute("data-bs-feed");
    var filter = document.getElementById('filters').getAttribute("data-filter");

    var data;
    if (node.classList.contains('bi-envelope-open')) {
        data = JSON.stringify({
            readed: false
        })
        if (filter == "read") {
            row.remove();
        }
        else {
            node.classList.remove('bi-envelope-open');
            node.classList.add('bi-check-lg');
        }
        if (!is_read_later_view()) {
            change_unread_counter(feed_id, 1);
        }
    }
    else {
        data = JSON.stringify({readed: true})
        if (filter == "unread") {
            row.remove();
        }
        else {
            node.classList.remove('bi-check-lg');
            node.classList.add('bi-envelope-open');
        }
        if (!is_read_later_view()) {
            change_unread_counter(feed_id, -1);
        }
    }

    // sends the updates to the server
    fetch(prefix + API_ROOT + "article/" + article_id, {
      method: "PUT",
      headers: {
        'Content-Type': 'application/json',
      },
      body: data
    }).then(res => {
      console.log("Request complete! response:", res);
    }).catch((error) => {
      console.error('Error:', error);
    });;
});


// Mark an article as read or unread from the article page
var nodes = document.getElementsByClassName('readed-article-page');
Array.prototype.map.call(nodes, function(node) {
    node.onclick = function() {
      var article_id = node.parentNode.parentNode.parentNode.getAttribute("data-article");

      var data;
      if (node.classList.contains('fa-square-o')) {
        data = JSON.stringify({readed: false})
        node.classList.remove('fa-square-o');
        node.classList.add('fa-check-square-o');
      }
      else {
        data = JSON.stringify({readed: true})
        node.classList.remove('fa-check-square-o');
        node.classList.add('fa-square-o');
      }

      // sends the updates to the server
      fetch(API_ROOT + "article/" + article_id, {
        method: "PUT",
        headers: {
          'Content-Type': 'application/json',
        },
        body: data
      }).then(res => {
        console.log("Request complete! response:", res);
      }).catch((error) => {
        console.error('Error:', error);
      });;
    }
});



// Like or unlike an article (event-delegated so it also works for rows added
// by infinite scroll).
document.addEventListener("click", function(event) {
    var node = event.target.closest(".like");
    if (!node) return;
    var row = node.closest("[data-article]");
    if (!row) return;
    const article_id = row.getAttribute("data-article");
    var data;
    var parent = node.parentNode;
    if (node.classList.contains("bi-star-fill")) {
        data = JSON.stringify({like: false});
        node.classList.remove('bi-star-fill');
        node.classList.add('bi-star');
        if (parent.classList.contains('text-warning')) {
            parent.classList.replace('text-warning', 'text-muted');
        }
        if(window.location.pathname.indexOf('/favorites') != -1) {
            row.remove();
        }
    }
    else {
        data = JSON.stringify({like: true})
        node.classList.remove('bi-star');
        node.classList.add('bi-star-fill');
        if (parent.classList.contains('text-muted')) {
            parent.classList.replace('text-muted', 'text-warning');
        }
    }

    // sends the updates to the server
    fetch(prefix + API_ROOT + "article/" + article_id, {
      method: "PUT",
      headers: {
        'Content-Type': 'application/json',
      },
      body: data
    }).then(res => {
      console.log("Request complete! response:", res);
    }).catch((error) => {
      console.error('Error:', error);
    });;
});



// Set aside an article to read later, or remove it from read later
// (event-delegated so it also works for rows added by infinite scroll and for
// the article page).
document.addEventListener("click", function(event) {
    var node = event.target.closest(".read-later-option");
    if (!node) return;
    var container = node.closest("[data-article]");
    if (!container) return;
    var article_id = container.getAttribute("data-article");
    var feed_id = container.getAttribute("data-bs-feed");
    var days = parseInt(node.dataset.days, 10);

    var dropdown = node.closest(".dropdown");
    var icon = dropdown.querySelector(".read-later-toggle");
    // Rows are only removed on the home page list, never on the article page.
    var row = node.closest("tr.article");

    if (days > 0) {
        icon.classList.remove("bi-clock");
        icon.classList.add("bi-clock-fill");
        dropdown.querySelectorAll(".read-later-cancel").forEach(function(el) {
            el.classList.remove("d-none");
        });
        if (row && !is_read_later_view()) {
            var filter = document.getElementById("filters").getAttribute("data-filter");
            if (filter == "unread") {
                row.remove();
                change_unread_counter(feed_id, -1);
            }
        }
    }
    else {
        icon.classList.remove("bi-clock-fill");
        icon.classList.add("bi-clock");
        dropdown.querySelectorAll(".read-later-cancel").forEach(function(el) {
            el.classList.add("d-none");
        });
        if (row && is_read_later_view()) {
            row.remove();
            change_unread_counter(feed_id, 1);
        }
    }

    // sends the updates to the server
    var csrf_token = document.querySelector('meta[name="csrf-token"]').content;
    fetch(prefix + "/article/read_later/" + article_id, {
      method: "POST",
      headers: {
        'X-CSRFToken': csrf_token,
      },
      body: new URLSearchParams({days: days})
    }).then(res => {
      console.log("Request complete! response:", res);
    }).catch((error) => {
      console.error('Error:', error);
    });
});


    // Delete all duplicate articles (used in the page /duplicates)
    var nodes = document.getElementsByClassName('delete-all');
    Array.prototype.forEach.call(nodes, function(node) {
      node.onclick = function() {
        var data = [];

        // get the column index of the header cell
        var th = node.closest("th");
        var columnNo = Array.prototype.indexOf.call(th.parentNode.children, th);

        // select all rows of the table body
        var table = node.closest("table");
        var rows = table.querySelectorAll("tbody tr");

        rows.forEach(function(row) {
          var cell = row.children[columnNo];
          if (cell && cell.id) {
            data.push(parseInt(cell.id));
            row.removeChild(cell); // remove just the cell
          }
        });

        data = JSON.stringify(data);

        // sends the updates to the server
        fetch(prefix + API_ROOT + "articles", {
          method: "DELETE",
          headers: {
            'Content-Type': 'application/json',
          },
          body: data
        }).then(res => {
          console.log("Request complete! response:", res);
        }).catch((error) => {
          console.error('Error:', error);
        });
      }
    });
