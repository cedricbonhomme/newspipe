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
        if(this.props.icon_url){
            icon = (<img width="16px" src={this.props.icon_url} />);
        } else {
            icon = <Glyphicon glyph="ban-circle" />;
        }
        if(this.props.unread){
            badge_unread = <Badge pullRight>{this.props.unread}</Badge>;
        }
        var classes = "nav-feed";
        if(this.props.active) {
            classes += " bg-primary";
        }
        if(this.props.error_count >= 6) {
            classes += " bg-danger";
        } else if(this.props.error_count > 3) {
            classes += " bg-warning";
        }
        var title = <span className="title">{this.props.title}</span>;
        return (<li className={classes} onClick={this.handleClick}>
                    {icon}{title}{badge_unread}
                </li>
        );
    },
    handleClick: function() {
        MiddlePanelActions.setFeedFilter(this.props.feed_id);
    },
});

var Category = React.createClass({
    propTypes: {category_id: React.PropTypes.number,
                active_type: React.PropTypes.string,
                active_id: React.PropTypes.number},
    render: function() {
        var classes = "nav-cat";
        if((this.props.active_type == 'category_id'
            || this.props.category_id == null)
           && this.props.active_id == this.props.category_id) {
            classes += " bg-primary";
        }
        return (<li className={classes} onClick={this.handleClick}>
                    {this.props.children}
                </li>
        );
    },
    handleClick: function(evnt) {
        // hack to avoid selection when clicking on folding icon
        if(!evnt.target.classList.contains('glyphicon')) {
            if(this.props.category_id != null) {
                MiddlePanelActions.setCategoryFilter(this.props.category_id);
            } else {
                MiddlePanelActions.removeParentFilter();
            }
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
        if(this.state.unfolded) {
            // filtering according to this.props.filter
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
                              active_id={this.props.active_id}
                              active_type={this.props.active_type}>
                        {ctrl}<h4>{this.props.name}</h4>{unread}
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
            error_button = (
                    <Button active={this.props.filter == "error"}
                            title="Some of your feeds are in error, click here to list them"
                            onMouseDown={this.setErrorFilter}
                            bsSize="small" bsStyle="warning">
                        <Glyphicon glyph="exclamation-sign" />
                    </Button>
            );
        }
        return (<ButtonGroup className="nav nav-sidebar">
                    <Button active={this.props.filter == "all"}
                            title="Display all feeds"
                            onMouseDown={this.setAllFilter} bsSize="small">
                        <Glyphicon glyph="menu-hamburger" />
                    </Button>
                    <Button active={this.props.filter == "unread"}
                            title="Display only feed with unread article"
                            onMouseDown={this.setUnreadFilter}
                            bsSize="small">
                        <Glyphicon glyph="unchecked" />
                    </Button>
                    {error_button}
                </ButtonGroup>
        );
    },
    setAllFilter: function() {
        MenuActions.setFilter("all");
    },
    setUnreadFilter: function() {
        MenuActions.setFilter("unread");
    },
    setErrorFilter: function() {
        MenuActions.setFilter("error");
    },
});

var Menu = React.createClass({
    getInitialState: function() {
        return {filter: 'all', categories: [], all_unread_count: 0,
                active_type: null, active_id: null};
    },
    render: function() {
        var state = this.state;
        var rmPrntFilt = (
                <ul className="nav nav-sidebar">
                    <Category category_id={null}
                              active_id={this.state.active_id}
                              active_type={this.state.active_type}>
                        <h4>All</h4>
                    </Category>
                </ul>
        );

        return (<Col xsHidden smHidden md={3} lg={2} data-spy="affix"
                     id="menu" className="show-grid sidebar">
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
