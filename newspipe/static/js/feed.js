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
