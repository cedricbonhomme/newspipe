var React = require('react');
var createReactClass = require('create-react-class');
var Col = require('react-bootstrap/lib/Col');
var Badge = require('react-bootstrap/lib/Badge');
var Button = require('react-bootstrap/lib/Button');
var ButtonGroup = require('react-bootstrap/lib/ButtonGroup');
var Glyphicon = require('react-bootstrap/lib/Glyphicon');
var PropTypes = require('prop-types');

var MenuStore = require('../stores/MenuStore');
var MenuActions = require('../actions/MenuActions');
var MiddlePanelActions = require('../actions/MiddlePanelActions');

var FeedItem = createReactClass({
    propTypes: {feed_id: PropTypes.number.isRequired,
                title: PropTypes.string.isRequired,
                unread: PropTypes.number.isRequired,
                error_count: PropTypes.number.isRequired,
                icon_url: PropTypes.string,
                active: PropTypes.bool.isRequired,
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
        if(this.props.error_count >= MenuStore._datas.max_error) {
            classes += " bg-danger";
        } else if(this.props.error_count > MenuStore._datas.error_threshold) {
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

var Category = createReactClass({
    propTypes: {category_id: PropTypes.number,
                active_type: PropTypes.string,
                active_id: PropTypes.number},
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

var CategoryGroup = createReactClass({
    propTypes: {cat_id: PropTypes.number.isRequired,
                filter: PropTypes.string.isRequired,
                active_type: PropTypes.string,
                active_id: PropTypes.number,
                name: PropTypes.string.isRequired,
                feeds: PropTypes.array.isRequired,
                unread: PropTypes.number.isRequired,
                folded: PropTypes.bool,
    },
    getInitialState: function() {
        return {folded: false};
    },
    componentWillReceiveProps: function(nextProps) {
        if(nextProps.folded != null) {
            this.setState({folded: nextProps.folded});
        }
    },
    render: function() {
        // hidden the no category if empty
        if(!this.props.cat_id && !this.props.feeds.length) {
            return <ul className="hidden" />;
        }
        var filter = this.props.filter;
        var a_type = this.props.active_type;
        var a_id = this.props.active_id;
        if(!this.state.folded) {
            // filtering according to this.props.filter
            var feeds = this.props.feeds.filter(function(feed) {
                if (filter == 'unread' && feed.unread <= 0) {
                    return false;
                } else if (filter == 'error' && feed.error_count <= MenuStore._datas.error_threshold) {
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
        if(this.props.unread) {
            unread = <Badge pullRight>{this.props.unread}</Badge>;
        }
        var ctrl = (<Glyphicon onClick={this.toggleFolding}
                        glyph={this.state.folded?"menu-right":"menu-down"} />
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
    toggleFolding: function(evnt) {
        this.setState({folded: !this.state.folded});
        evnt.stopPropagation();
    },
});

var MenuFilter = createReactClass({
    propTypes: {feed_in_error: PropTypes.bool,
                filter: PropTypes.string.isRequired},
    getInitialState: function() {
        return {allFolded: false};
    },
    render: function() {
        var error_button = null;
        if (this.props.feed_in_error) {
            error_button = (
                    <Button active={this.props.filter == "error"}
                            title="Some of your feeds are in error, click here to list them"
                            onClick={this.setErrorFilter}
                            bsSize="small" bsStyle="warning">
                        <Glyphicon glyph="exclamation-sign" />
                    </Button>
            );
        }
        if(this.state.allFolded) {
            var foldBtnTitle = "Unfold all categories";
            var foldBtnGlyph = "option-horizontal";
        } else {
            var foldBtnTitle = "Fold all categories";
            var foldBtnGlyph = "option-vertical";
        }
        return (<div>
                <ButtonGroup className="nav nav-sidebar">
                    <Button active={this.props.filter == "all"}
                            title="Display all feeds"
                            onClick={this.setAllFilter} bsSize="small">
                        <Glyphicon glyph="menu-hamburger" />
                    </Button>
                    <Button active={this.props.filter == "unread"}
                            title="Display only feed with unread article"
                            onClick={this.setUnreadFilter}
                            bsSize="small">
                        <Glyphicon glyph="unchecked" />
                    </Button>
                    {error_button}
                </ButtonGroup>
                <ButtonGroup className="nav nav-sidebar">
                    <Button onClick={MenuActions.reload}
                            title="Refresh all feeds" bsSize="small">
                        <Glyphicon glyph="refresh" />
                    </Button>
                </ButtonGroup>
                <ButtonGroup className="nav nav-sidebar">
                    <Button title={foldBtnTitle} bsSize="small"
                            onClick={this.toggleFold}>
                        <Glyphicon glyph={foldBtnGlyph} />
                    </Button>
                </ButtonGroup>
                </div>
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
    toggleFold: function() {
        this.setState({allFolded: !this.state.allFolded}, function() {
            MenuActions.toggleAllFolding(this.state.allFolded);
        }.bind(this));
    },
});

var Menu = createReactClass({
    getInitialState: function() {
        return {filter: 'unread', categories: {}, feeds: {},
                all_folded: false, active_type: null, active_id: null};
    },
    render: function() {
        var feed_in_error = false;
        var rmPrntFilt = (
                <ul className="nav nav-sidebar">
                    <Category category_id={null}
                              active_id={this.state.active_id}
                              active_type={this.state.active_type}>
                        <h4>All</h4>
                    </Category>
                </ul>
        );
        var categories = [];
        for(var index in this.state.categories_order) {
            var cat_id = this.state.categories_order[index];
            var feeds = [];
            var unread = 0;
            this.state.categories[cat_id].feeds.map(function(feed_id) {
                if(this.state.feeds[feed_id].error_count > MenuStore._datas.error_threshold) {
                    feed_in_error = true;
                }
                unread += this.state.feeds[feed_id].unread;
                feeds.push(this.state.feeds[feed_id]);
            }.bind(this));
            categories.push(<CategoryGroup key={"c" + cat_id} feeds={feeds}
                                    filter={this.state.filter}
                                    active_type={this.state.active_type}
                                    active_id={this.state.active_id}
                                    name={this.state.categories[cat_id].name}
                                    cat_id={this.state.categories[cat_id].id}
                                    folded={this.state.all_folded}
                                    unread={unread} />);
        }

        return (<Col xsHidden smHidden md={3} lg={2}
                     id="menu" className="sidebar">
                    <MenuFilter filter={this.state.filter}
                                feed_in_error={feed_in_error} />
                    {rmPrntFilt}
                    {categories}
                </Col>
        );
    },
    componentDidMount: function() {
        var setFilterFunc = null;
        var id = null;
        if(window.location.search.substring(1)) {
            var args = window.location.search.substring(1).split('&');
            args.map(function(arg) {
                if (arg.split('=')[0] == 'at' && arg.split('=')[1] == 'c') {
                    setFilterFunc = MiddlePanelActions.setCategoryFilter;
                } else if (arg.split('=')[0] == 'at' && arg.split('=')[1] == 'f') {
                    setFilterFunc = MiddlePanelActions.setFeedFilter;

                } else if (arg.split('=')[0] == 'ai') {
                    id = parseInt(arg.split('=')[1]);
                }
            });
        }
        MenuActions.reload(setFilterFunc, id);
        MenuStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        MenuStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        var datas = MenuStore.getAll();
        this.setState({filter: datas.filter,
                       feeds: datas.feeds,
                       categories: datas.categories,
                       categories_order: datas.categories_order,
                       active_type: datas.active_type,
                       active_id: datas.active_id,
                       all_folded: datas.all_folded});
    },
});

module.exports = Menu;
