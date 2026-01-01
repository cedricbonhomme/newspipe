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


// Mark an article as read or unread from the home page
var nodes = document.getElementsByClassName('readed');
Array.prototype.map.call(nodes, function(node) {
    node.onclick = function() {
      var article_id = node.parentNode.parentNode.parentNode.getAttribute("data-article");
      var feed_id = node.parentNode.parentNode.parentNode.getAttribute("data-bs-feed");
      var filter = document.getElementById('filters').getAttribute("data-filter");

      var data;
      if (node.classList.contains('bi-envelope-open')) {
          data = JSON.stringify({
              readed: false
          })
          if (filter == "read") {
              node.parentNode.parentNode.parentNode.remove();
          }
          else {
              // here, filter == "all"
              // node.parentNode.parentNode.parentNode.children("td:nth-child(2)").css( "font-weight", "bold" );
              node.classList.remove('bi-envelope-open');
              node.classList.add('bi-envelope');
          }
          change_unread_counter(feed_id, 1);
      }
      else {
          data = JSON.stringify({readed: true})
          if (filter == "unread") {
              node.parentNode.parentNode.parentNode.remove();
          }
          else {
              // here, filter == "all"
              // node.parentNode.parentNode.parentNode.children("td:nth-child(2)").css( "font-weight", "normal" );
              node.classList.remove('bi-envelope');
              node.classList.add('bi-envelope-open');
          }
          change_unread_counter(feed_id, -1);
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
    }
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



// Like or unlike an article
var nodes = document.getElementsByClassName('like');
Array.prototype.map.call(nodes, function(node) {
    node.onclick = function() {
      const container = document.querySelector(".article");
      const article_id = container.getAttribute("data-article");
      console.log(article_id);
      var data;
      if (node.classList.contains("bi-star-fill")) {
          data = JSON.stringify({like: false});
          node.classList.remove('bi-star-fill');
          node.classList.add('bi-star');
          if(window.location.pathname.indexOf('/favorites') != -1) {
              node.parentNode.parentNode.parentNode.remove();
          }
      }
      else {
          data = JSON.stringify({like: true})
          node.classList.remove('bi-star');
          node.classList.add('bi-star-fill');
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
    }
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
