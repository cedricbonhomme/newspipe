var node = document.getElementById('add-feed-filter-row');
if (node != null) {
  node.onclick = function() {
    document.getElementById('filters-container').innerHTML +=
          '<div class="row row-cols-md-auto g-5 align-items-center">'
          + '<div class="col">'
          + '    <input value="-" type="button" class="form-control del-feed-filter-row" />'
          + '</div>'
          + '<div class="col">'
          + '    <select name="type" class="form-select">'
          + '        <option value="simple match" selected>simple match</option>'
          + '        <option value="regex">regex</option>'
          + '    </select>'
          + '</div>'
          + '<div class="col">'
          + '    <input type="text" class="form-control" name="pattern" />'
          + '</div>'
          + '<div class="col">'
          + '    <select name="action_on" class="form-select">'
          + '        <option value="match" selected>match</option>'
          + '        <option value="no match">no match</option>'
          + '    </select>'
          + '</div>'
          + '<div class="col">'
          + '    <select name="action" class="form-select">'
          + '        <option value="mark as read" selected>mark as read</option>'
          + '        <option value="mark as favorite">mark as favorite</option>'
          + '    </select>'
          + '</div>'
          + '</div><br />';
  }
}

var nodes = document.getElementsByClassName('del-feed-filter-row');
Array.prototype.map.call(nodes, function(node) {
    node.onclick = function() {
      node.parentNode.parentNode.remove();
    }
})
