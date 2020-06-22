var node = document.getElementById('add-feed-filter-row');
if (node != null) {
  node.onclick = function() {
    document.getElementById('filters-container').innerHTML = 
          '<div class="form-group">'
          + '    <input value="-" type="button" class="form-control del-feed-filter-row" />'
          + '    <select name="type" class="form-control">'
          + '        <option value="simple match" selected>simple match</option>'
          + '        <option value="regex">regex</option>'
          + '    </select>'
          + '    <input type="text" class="form-control"  name="pattern" />'
          + '    <select name="action_on" class="form-control">'
          + '        <option value="match" selected>match</option>'
          + '        <option value="no match">no match</option>'
          + '    </select>'
          + '    <select name="action" class="form-control">'
          + '        <option value="mark as read" selected>mark as read</option>'
          + '        <option value="mark as favorite">mark as favorite</option>'
          + '    </select>'
          + '</div>';  
  }  
}

var nodes = document.getElementsByClassName('del-feed-filter-row');
Array.prototype.map.call(nodes, function(node) {
    node.onclick = function() {
      node.parentNode.remove();
    }
})


// Delete a feed
var nodes = document.getElementsByClassName('delete-feed');
Array.prototype.map.call(nodes, function(node) {
    node.onclick = function() {
    var r = confirm('You are going to delete this feed.');

    if (r == true) {
        var feed_id = node.parentNode.parentNode.parentNode.getAttribute("data-feed");
        node.parentNode.parentNode.parentNode.remove();
        // $('.feed-menu[data-feed='+feed_id+']').remove();

        // sends the updates to the server
        fetch(API_ROOT + "feed/" + feed_id, {
          method: "DELETE", 
          headers: {
            'Content-Type': 'application/json',
          },
        }).then(res => {
          console.log("Request complete! response:", res);
        }).catch((error) => {
          console.error('Error:', error);
        });;
    }
  }
})
