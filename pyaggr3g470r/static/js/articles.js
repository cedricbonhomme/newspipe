/*!
* pyAggr3g470r - A Web based news aggregator.
* Copyright (C) 2010-2014  Cédric Bonhomme - http://cedricbonhomme.org/
*
* For more information : https://bitbucket.org/cedricbonhomme/pyaggr3g470r/
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

if (typeof jQuery === 'undefined') { throw new Error('Requires jQuery') }

function change_unread_counter(feed_id, increment) {
    var new_value = parseInt($("#unread-"+feed_id).text()) + increment;
    $("#unread-"+feed_id).text(new_value);
    $("#total-unread").text(parseInt($("#total-unread").text()) + increment);
    if (new_value == 0) {
        $("#unread-"+feed_id).hide();
    } else {
        $("#unread-"+feed_id).show();
    }
}

+function ($) {

    // Mark an article as read when it is opened in a new table
    $('.open-article').on('click', function(e) {
      var feed_id = $(this).parent().parent().attr("data-feed");
      var filter = $('#filters').attr("data-filter");
      if (filter == "unread") {
        $(this).parent().parent().remove();
        change_unread_counter(feed_id, -1);
      }
    });

    // Mark an article as read or unread.
    $('.readed').on('click', function() {
        var article_id = $(this).parent().parent().parent().attr("data-article");
        var feed_id = $(this).parent().parent().parent().attr("data-feed");
        var filter = $('#filters').attr("data-filter");

        var data;
        if ($(this).hasClass("glyphicon-unchecked")) {
            data = JSON.stringify({
                readed: false
                })
            if (filter == "read") {
                $(this).parent().parent().parent().remove();
            }
            else {
                // here, filter == "all"
                $(this).parent().parent().parent().children("td:nth-child(2)").css( "font-weight", "bold" );
                $(this).removeClass('glyphicon-unchecked').addClass('glyphicon-check');
            }
            change_unread_counter(feed_id, 1);
        }
        else {
            data = JSON.stringify({readed: true})
            if (filter == "unread") {
                $(this).parent().parent().parent().remove();
            }
            else {
                // here, filter == "all"
                $(this).parent().parent().parent().children("td:nth-child(2)").css( "font-weight", "normal" );
                $(this).removeClass('glyphicon-check').addClass('glyphicon-unchecked');
            }
            change_unread_counter(feed_id, -1);
        }

        // sends the updates to the server
        $.ajax({
            type: 'PUT',
            // Provide correct Content-Type, so that Flask will know how to process it.
            contentType: 'application/json',
            // Encode your data as JSON.
            data: data,
            // This is the type of data you're expecting back from the server.
            url: API_ROOT + "article/" + article_id,
            success: function (result) {
                //console.log(result);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                console.log(XMLHttpRequest.responseText);
            }
        });
    });



    // Like or unlike an article
    $('.like').on('click', function() {
        var article_id = $(this).parent().parent().parent().attr("data-article");

        var data;
        if ($(this).hasClass("glyphicon-star")) {
            data = JSON.stringify({like: false})
            $(this).removeClass('glyphicon-star').addClass('glyphicon-star-empty');
        }
        else {
            data = JSON.stringify({like: true})
            $(this).removeClass('glyphicon-star-empty').addClass('glyphicon-star');
        }

        // sends the updates to the server
        $.ajax({
            type: 'PUT',
            // Provide correct Content-Type, so that Flask will know how to process it.
            contentType: 'application/json',
            // Encode your data as JSON.
            data: data,
            // This is the type of data you're expecting back from the server.
            url: API_ROOT + "article/" + article_id,
            success: function (result) {
                //console.log(result);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                console.log(XMLHttpRequest.responseText);
            }
        });
    });

    // Delete an article
    $('.delete').on('click', function() {
        var feed_id = $(this).parent().parent().parent().attr("data-feed");
        var article_id = $(this).parent().parent().parent().attr("data-article");
        $(this).parent().parent().parent().remove();

        // sends the updates to the server
        $.ajax({
            type: 'DELETE',
            url: API_ROOT + "article/" + article_id,
            success: function (result) {
                change_unread_counter(feed_id, -1);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                console.log(XMLHttpRequest.responseText);
            }
        });
    });

    // Delete all duplicate articles (used in the page /duplicates)
    $('.delete-all').click(function(){
        var data = [];

        var columnNo = $(this).parent().index();
        $(this).closest("table")
            .find("tr td:nth-child(" + (columnNo+1) + ")")
            .each(function(line, column) {
                data.push(parseInt(column.id));
            }).remove();

        data = JSON.stringify(data);

        // sends the updates to the server
        $.ajax({
            type: 'DELETE',
            // Provide correct Content-Type, so that Flask will know how to process it.
            contentType: 'application/json',
            data: data,
            url: API_ROOT + "articles",
            success: function (result) {
                //console.log(result);
            },
            error: function(XMLHttpRequest, textStatus, errorThrown){
                console.log(XMLHttpRequest.responseText);
            }
        });

    });

}(jQuery);
