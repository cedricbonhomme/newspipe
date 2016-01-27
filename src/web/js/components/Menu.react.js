var React = require('react');
var Col = require('react-bootstrap/Col');
var Badge = require('react-bootstrap/Badge');
var Button = require('react-bootstrap/Button');
var ButtonGroup = require('react-bootstrap/ButtonGroup');
var Glyphicon = require('react-bootstrap/Glyphicon');

var MenuStore = require('../stores/MenuStore');
var MenuActions = require('../actions/MenuActions');
var MiddlePanelActions = require('../actions/MiddlePanelActions');

var FeedItem = React.createClass({
    propTypes: {feed_id: React.PropTypes.number.isRequired,
                title: React.PropTypes.string.isRequired,
                unread: React.PropTypes.number.isRequired,
                error_count: React.PropTypes.number.isRequired,
                icon_url: React.PropTypes.string,
                active: React.PropTypes.bool.isRequired,
    },
    render: function() {
        var icon = null;
        var badge_unread = null;
        var style = null;
        if(this.props.icon_url){
            icon = (<img width="16px" src={this.props.icon_url} />);
        } else {
            icon = <Glyphicon glyph="ban-circle" />;
        }
        if(this.props.unread){
            badge_unread = <Badge pullRight>{this.props.unread}</Badge>;
        }
        if(this.props.error_count == 6) {
            style = "danger";
        } else if(this.props.error_count > 3) {
            style = "warning";
        }
        return (<li onClick={this.handleClick}>
                    {icon}{this.props.title}{badge_unread}
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
                active_type: React.PropTypes.string,
                active_id: React.PropTypes.number},
    render: function() {
        if(this.props.active_type == 'active_id'
           && this.props.active_id == this.props.category_id) {
            var classes = "success active";
        } else {
            var classes = "success";
        }
        return (<li className={classes}>
                    <h4 onClick={this.handleClick}>
                        {this.props.children}
                    </h4>
                </li>
        );
    },
    handleClick: function() {
        if(this.props.category_id != null) {
            MiddlePanelActions.setCategoryFilter(this.props.category_id);
        } else {
            MiddlePanelActions.removeParentFilter();
        }
    },
});

var CategoryGroup = React.createClass({
    propTypes: {cat_id: React.PropTypes.number.isRequired,
                filter: React.PropTypes.string.isRequired,
                active_type: React.PropTypes.string,
                active_id: React.PropTypes.number,
                name: React.PropTypes.string.isRequired,
                feeds: React.PropTypes.array.isRequired,
                unread: React.PropTypes.number.isRequired,
    },
    getInitialState: function() {
        return {unfolded: true};
    },
    render: function() {
        var filter = this.props.filter;
        var a_type = this.props.active_type;
        var a_id = this.props.active_id;
        // filtering according to this.props.filter
        if(this.state.unfolded) {
        var feeds = this.props.feeds.filter(function(feed) {
            if (filter == 'unread' && feed.unread <= 0) {
                return false;
            } else if (filter == 'error' && feed.error_count <= 3) {
                return false;
            }
            return true;
        }).sort(function(feed_a, feed_b){
            return feed_b.unread - feed_a.unread;
        }).map(function(feed) {
            return (<FeedItem key={"f" + feed.id} feed_id={feed.id}
                              title={feed.title} unread={feed.unread}
                              error_count={feed.error_count}
                              active={a_type == 'feed_id' && a_id == feed.id}
                              icon_url={feed.icon_url} />
            );
        });
        } else {
            var feeds = [];
        }
        var unread = null;
        if(this.props.unread){
            unread = <Badge pullRight>{this.props.unread}</Badge>;
        }
        var ctrl = (<Glyphicon onMouseDown={this.toggleFolding} pullLeft
                        glyph={this.state.unfolded?"menu-down":"menu-right"} />
                    );

        return (<ul className="nav nav-sidebar">
                    <Category category_id={this.props.cat_id}
                              active_type={this.props.active_id}
                              active_type={this.props.active_type}>
                        {ctrl} <strong>{this.props.name}</strong> {unread}
                    </Category>
                    {feeds}
                </ul>
        );
    },
    handleClick: function() {
        MiddlePanelActions.setCategoryFilter(this.props.cat_id);
    },
    toggleFolding: function(evnt) {
        this.setState({unfolded: !this.state.unfolded});
        evnt.stopPropagation();
    },
});

var MenuFilter = React.createClass({
    propTypes: {feed_in_error: React.PropTypes.bool,
                filter: React.PropTypes.string.isRequired},
    render: function() {
        var error_button = null;
        if (this.props.feed_in_error) {
            error_button = (<Button active={this.props.filter == "error"}
                                onMouseDown={() => MenuActions.setFilter("error")}
                                bsSize="small" bsStyle="warning">Error</Button>
            );
        }
        return (<ButtonGroup className="nav nav-sidebar">
                    <Button active={this.props.filter == "all"}
                            onMouseDown={() => MenuActions.setFilter("all")}
                            bsSize="small">All</Button>
                    <Button active={this.props.filter == "unread"}
                            onMouseDown={() => MenuActions.setFilter("unread")}
                            bsSize="small">Unread</Button>
                    {error_button}
                </ButtonGroup>
        );
    },
});

var Menu = React.createClass({
    getInitialState: function() {
        return {filter: 'all', categories: [], all_unread_count: 0,
                active_type: null, active_id: null};
    },
    render: function() {
        var state = this.state;
        if (this.state.active_type == null || this.state.active_id == null) {
            var all_classname = "success active";
        } else {
            var all_classname = "success";
        }
        var rmPrntFilt = (
                <ul className="nav nav-sidebar">
                    <Category category_id={null}
                              active_type={this.props.active_id}
                              active_type={this.props.active_type}>
                        <strong>All</strong>
                    </Category>
                </ul>
        );

        return (<Col xsHidden smHidden md={3} lg={2} className="show-grid sidebar">
                    <MenuFilter filter={this.state.filter}
                                feed_in_error={this.state.feed_in_error} />
                    {rmPrntFilt}
                    {this.state.categories.map(function(category){
                        return (<CategoryGroup key={"c" + category.id}
                                               filter={state.filter}
                                               active_type={state.active_type}
                                               active_id={state.active_id}
                                               cat_id={category.id}
                                               feeds={category.feeds}
                                               name={category.name}
                                               unread={category.unread} />);
                        })}
                </Col>
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
                       active_type: datas.active_type,
                       active_id: datas.active_id,
                       feed_in_error: datas.feed_in_error,
                       all_unread_count: datas.all_unread_count});
    },
});

module.exports = Menu;
