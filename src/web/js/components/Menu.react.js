var React = require('react');
var Row = require('react-bootstrap/lib/Row');
var Badge = require('react-bootstrap/lib/Badge');
var Button = require('react-bootstrap/lib/Button');
var ButtonGroup = require('react-bootstrap/lib/ButtonGroup');
var ListGroup = require('react-bootstrap/lib/ListGroup');
var ListGroupItem = require('react-bootstrap/lib/ListGroupItem');
var Glyphicon = require('react-bootstrap/lib/Glyphicon');

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
        return (<ListGroupItem onMouseDown={this.handleClick} bsStyle={style}
                               href="#" active={this.props.active}>
                    {icon}{this.props.title}{badge_unread}
                </ListGroupItem>
        );
    },
    handleClick: function() {
        MiddlePanelActions.setFeedFilter(this.props.feed_id);
    },
});

var Category = React.createClass({
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
        var active = a_type == 'category_id' && a_id == this.props.cat_id;
        var ctrl = (<Glyphicon onMouseDown={this.toggleFolding} pullLeft
                        glyph={this.state.unfolded?"menu-down":"menu-right"} />
                    );

        return (<ListGroup>
                    <ListGroupItem href="#" bsStyle="success"
                                   active={active}
                                   onMouseDown={this.handleClick}>
                        {ctrl} <strong>{this.props.name}</strong> {unread}
                    </ListGroupItem>
                    {feeds}
                </ListGroup>
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
    getInitialState: function() {
        return {filter: 'all', feed_in_error: false};
    },
    render: function() {
        var error_button = null;
        if (this.state.feed_in_error) {
            error_button = (<Button active={this.state.filter == "error"}
                                onMouseDown={() => this.setFilter("error")}
                                bsSize="small" bsStyle="warning">Error</Button>
            );
        }
        return (<Row className="show-grid">
                    <ButtonGroup>
                        <Button active={this.state.filter == "all"}
                                onMouseDown={() => this.setFilter("all")}
                                bsSize="small">All</Button>
                        <Button active={this.state.filter == "unread"}
                                onMouseDown={() => this.setFilter("unread")}
                                bsSize="small">Unread</Button>
                        {error_button}
                    </ButtonGroup>
                </Row>
        );
    },
    setFilter: function(filter) {
        this.setState({filter: filter});
        MenuActions.setFilter(filter);
    },
    componentDidMount: function() {
        MenuStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        MenuStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        this.setState({feed_in_error: MenuStore._datas.feed_in_error});
    },
});

var Menu = React.createClass({
    getInitialState: function() {
        return {filter: 'all', categories: [], all_unread_count: 0,
                active_type: null, active_id: null};
    },
    render: function() {
        var state = this.state;
        var rmPrntFilt = (<ListGroupItem href="#" bsStyle="success"
                active={this.state.active_type == null
                        || this.state.active_id == null}
                onMouseDown={MiddlePanelActions.removeParentFilter}
                header="All"></ListGroupItem>);

        return (<Row className="show-grid">
                    <ListGroup>{rmPrntFilt}</ListGroup>
                    {this.state.categories.map(function(category){
                        return (<Category key={"c" + category.id}
                                            filter={state.filter}
                                            active_type={state.active_type}
                                            active_id={state.active_id}
                                            cat_id={category.id}
                                            feeds={category.feeds}
                                            name={category.name}
                                            unread={category.unread} />);
                        })}
                </Row>
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
                       all_unread_count: datas.all_unread_count});
    },
});

module.exports = {Menu: Menu, MenuFilter: MenuFilter};
