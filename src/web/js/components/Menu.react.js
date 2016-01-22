var React = require('react');
var Button = require('react-bootstrap/lib/Button');
var ButtonGroup = require('react-bootstrap/lib/ButtonGroup');
var Badge = require('react-bootstrap/lib/Badge');

var MenuStore = require('../stores/MenuStore');
var MenuActions = require('../actions/MenuActions');
var MiddlePanelActions = require('../actions/MiddlePanelActions');

var FeedItem = React.createClass({
    propTypes: {feed_id: React.PropTypes.number.isRequired,
                title: React.PropTypes.string.isRequired,
                unread: React.PropTypes.number.isRequired,
                error_count: React.PropTypes.number.isRequired,
                icon_url: React.PropTypes.string,
    },
    render: function() {
        var icon = null;
        var badge_unread = null;
        var badge_error = null;
        if(this.props.icon_url){
            icon = (<img width="16px" src={this.props.icon_url} />);
        } else {
            icon = (<span className="glyphicon glyphicon-ban-circle" />);
        }
        if(this.props.unread){
            badge_unread = <Badge pullRight>{this.props.unread}</Badge>;
        }
        if(this.props.error_count == 6) {
            badge_unread = <Badge pullRight error>error</Badge>;
        } else if(this.props.error_count > 3) {
            badge_unread = <Badge pullRight warning>warn</Badge>;
        }
        return (<li onMouseDown={this.handleClick}>
                    {icon}{this.props.title}{badge_unread}{badge_error}
                </li>
        );
    },
    handleClick: function() {
        MiddlePanelActions.setFeedFilter(this.props.feed_id);
    },
});

var Category = React.createClass({
    propTypes: {category_id: React.PropTypes.number.isRequired,
                filter: React.PropTypes.string.isRequired,
                name: React.PropTypes.string.isRequired,
                feeds: React.PropTypes.array.isRequired,
                unread: React.PropTypes.number.isRequired,
    },
    render: function() {
        var filter = this.props.filter;
        // filtering according to this.props.filter
        var feeds = this.props.feeds.filter(function(feed) {
            if (filter == 'unread' && feed.unread <= 0) {return false;}
            else if (filter == 'error' && feed.error_count <= 3){return false;}
            return true;
        }).sort(function(feed_a, feed_b){
            return feed_b.unread - feed_a.unread;
        }).map(function(feed) {
            return (<FeedItem key={"feed" + feed.id} feed_id={feed.id}
                              title={feed.title} unread={feed.unread}
                              error_count={feed.error_count}
                              icon_url={feed.icon_url} />);
        });
        var unread = undefined;
        if(this.props.unread){
            unread = (<span className="badge pull-right">
                            {this.props.unread}
                      </span>);
        }
        return (<div>
                    <h3 onMouseDown={this.handleClick}>
                        {this.props.name} {unread}
                    </h3>
                    <ul className="nav nav-sidebar">{feeds}</ul>
                </div>
        );
    },
    handleClick: function() {
        MiddlePanelActions.setCategoryFilter(this.props.category_id);
    },
});

var Menu = React.createClass({
    getInitialState: function() {
        return {filter: 'all', categories: [],
                feed_in_error: false, all_unread_count: 0};
    },
    render: function() {
        var filter = this.state.filter;
        var error_button = null;
        if (this.state.feed_in_error) {
            error_button = (<Button active={this.state.filter == "error"}
                                onMouseDown={MenuActions.setFilterError}
                                bsSize="small" bsStyle="warning">Error</Button>
            );
        }
        return (<div id="sidebar" data-spy="affix" role="navigation"
                     className="col-md-2 sidebar sidebar-offcanvas pre-scrollable hidden-sm hidden-xs affix">
                    <ButtonGroup>
                        <Button active={this.state.filter == "all"}
                                onMouseDown={MenuActions.setFilterAll}
                                bsSize="small">All</Button>
                        <Button active={this.state.filter == "unread"}
                                onMouseDown={MenuActions.setFilterUnread}
                                bsSize="small">Unread</Button>
                        {error_button}
                   </ButtonGroup>
                    {this.state.categories.map(function(category){
                        return (<Category key={"cat" + category.id}
                                          filter={filter}
                                          category_id={category.id}
                                          feeds={category.feeds}
                                          name={category.name}
                                          unread={category.unread} />);
                        })}

                </div>
        );
    },
    componentDidMount: function() {
        MenuActions.reload();
        MenuStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        MenuStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        var datas = MenuStore.getAll();
        this.setState({filter: datas.filter,
                       categories: datas.categories,
                       feed_in_error: datas.feed_in_error,
                       all_unread_count: datas.all_unread_count});
    },
});

module.exports = Menu;
