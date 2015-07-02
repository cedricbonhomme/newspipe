$('.container').on('click', '#add-feed-filter-row', function() {
    $('#filters-container').append(
        '<div class="col-sm-9">'
        + '    <input value="-" type="button" class="del-feed-filter-row" />'
        + '    <select name="type">'
        + '        <option value="simple match" selected>simple match</option>'
        + '        <option value="regex">regex</option>'
        + '    </select/>'
        + '    <input type="text" size="50%" name="pattern" />'
        + '    <select name="action_on">'
        + '        <option value="match" selected>match</option>'
        + '        <option value="no match">no match</option>'
        + '    </select/>'
        + '    <select name="action">'
        + '        <option value="mark as read" selected>mark as read</option>'
        + '        <option value="mark as favorite">mark as favorite</option>'
        + '    </select/>'
        + '</div>');
});
$('.container').on('click', '.del-feed-filter-row', function() {
    $(this).parent().remove();
});
