/*!
* Newspipe - A web news aggregator.
* Copyright (C) 2010-2020 Cédric Bonhomme - https://cedricbonhomme.org
*
* For more information: https://sr.ht/~cedric/newspipe
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

API_ROOT = '/api/v2.0/'


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


// Mark an article as read when it is opened in a new table
document.getElementsByClassName('open-article').onclick = function fun() {
  var feed_id = $(this).parentNode.parentNode.attr("data-feed");
  var filter = $('#filters').attr("data-filter");
  if (filter == "unread") {
    $(this).parentNode.parentNode.remove();
    change_unread_counter(feed_id, -1);
  }
};


// Mark an article as read or unread from the home page
var nodes = document.getElementsByClassName('readed');
Array.prototype.map.call(nodes, function(node) {
    node.onclick = function() {
      var article_id = node.parentNode.parentNode.parentNode.getAttribute("data-article");
      var feed_id = node.parentNode.parentNode.parentNode.getAttribute("data-feed");
      var filter = document.getElementById('filters').getAttribute("data-filter");

      var data;
      if (node.classList.contains('fa-square-o')) {
          data = JSON.stringify({
              readed: false
          })
          if (filter == "read") {
              node.parentNode.parentNode.parentNode.remove();
          }
          else {
              // here, filter == "all"
              // node.parentNode.parentNode.parentNode.children("td:nth-child(2)").css( "font-weight", "bold" );
              node.classList.remove('fa-square-o');
              node.classList.add('fa-check-square-o');
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
              node.classList.remove('fa-check-square-o');
              node.classList.add('fa-square-o');
          }
          change_unread_counter(feed_id, -1);
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
      var article_id = node.parentNode.parentNode.parentNode.getAttribute('data-article');
      var data;
      if (node.classList.contains("fa-star")) {
          data = JSON.stringify({like: false});
          node.classList.remove('fa-star');
          node.classList.add('fa-star-o');
          if(window.location.pathname.indexOf('/favorites') != -1) {
              node.parentNode.parentNode.parentNode.remove();
          }
      }
      else {
          data = JSON.stringify({like: true})
          node.classList.remove('fa-star-o');
          node.classList.add('fa-star');
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



    // Delete all duplicate articles (used in the page /duplicates)
    var nodes = document.getElementsByClassName('delete-all');
    Array.prototype.map.call(nodes, function(node) {
        node.onclick = function() {
        var data = [];

        var columnNo = node.parentNode.index();
        node.closest("table")
            .find("tr td:nth-child(" + (columnNo+1) + ")")
            .each(function(line, column) {
                data.push(parseInt(column.id));
            }).remove();

        data = JSON.stringify(data);

        // sends the updates to the server
        fetch(API_ROOT + "articles", {
          method: "DELETE", 
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
