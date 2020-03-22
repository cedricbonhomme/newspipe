$('.container').on('click', '#add-feed-filter-row', function() {
    $('#filters-container').append(
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
        + '</div>');
});
$('.container').on('click', '.del-feed-filter-row', function() {
    $(this).parent().remove();
});


// Delete a feed
$('.delete-feed').on('click', function() {
    var r = confirm('You are going to delete this feed.');

    if (r == true) {
        var feed_id = $(this).parent().parent().parent().attr("data-feed");
        $(this).parent().parent().parent().remove();
        $('.feed-menu[data-feed='+feed_id+']').remove();

        // sends the updates to the server
        $.ajax({
            type: 'DELETE',
            url: API_ROOT + "feed/" + feed_id,
            success: function (result) {
                // change_unread_counter(feed_id, -1);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                console.log(XMLHttpRequest.responseText);
            }
        });
    }
});
