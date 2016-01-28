var React = require('react');
var Row = require('react-bootstrap/Row');
var Button = require('react-bootstrap/Button');
var ButtonGroup = require('react-bootstrap/ButtonGroup');
var Glyphicon = require('react-bootstrap/Glyphicon');

var MiddlePanelStore = require('../stores/MiddlePanelStore');
var MiddlePanelActions = require('../actions/MiddlePanelActions');

var TableLine = React.createClass({
    propTypes: {article_id: React.PropTypes.number.isRequired,
                feed_title: React.PropTypes.string.isRequired,
                icon_url: React.PropTypes.string,
                title: React.PropTypes.string.isRequired,
                date: React.PropTypes.string.isRequired,
                read: React.PropTypes.bool.isRequired,
                liked: React.PropTypes.bool.isRequired,
    },
    getInitialState: function() {
        return {read: this.props.read, liked: this.props.liked};
    },
    render: function() {
        var liked = this.state.liked ? 'l' : '';
        var icon = null;
        if(this.props.icon_url){
            icon = (<img width="16px" src={this.props.icon_url} />);
        } else {
            icon = <Glyphicon glyph="ban-circle" />;
        }
        var title = (<a href={'/article/redirect/' + this.props.article_id}>
                        {icon} {this.props.feed_title}
                     </a>);
        var read = (<Glyphicon glyph={this.state.read?"check":"unchecked"}
                               onClick={this.toogleRead} />);
        var liked = (<Glyphicon glyph={this.state.liked?"star":"star-empty"}
                                onClick={this.toogleLike} />);
        return (<div className="list-group-item">
                    <h4>{title}</h4>
                    {read} {liked} {this.props.title}
                </div>
        );
    },
    toogleRead: function() {
        this.setState({read: !this.state.read});
        MiddlePanelActions.changeRead(this.props.category_id,
                this.props.feed_id, this.props.article_id, !this.state.read);
    },
    toogleLike: function() {
        this.setState({liked: !this.state.liked});
        MiddlePanelActions.changeLike(this.props.category_id,
                this.props.feed_id, this.props.article_id, !this.state.liked);
    },
});

var MiddlePanelSearchRow = React.createClass({
    getInitialState: function() {
        return {query: MiddlePanelStore._datas.query,
                search_title: MiddlePanelStore._datas.search_title,
                search_content: MiddlePanelStore._datas.search_content,
        };
    },
    render: function() {
        return (<Row>
                    <form onSubmit={this.launchSearch}>
                    <div className="input-group input-group-sm">
                        <span className="input-group-addon">
                            <span onClick={this.toogleSTitle}>Title</span>
                            <input id="search-title" type="checkbox"
                                   onChange={this.toogleSTitle}
                                   checked={this.state.search_title}
                                   aria-label="Search title" />
                        </span>
                        <span className="input-group-addon">
                            <span onClick={this.toogleSContent}>Content</span>
                            <input id="search-content" type="checkbox"
                                   onChange={this.toogleSContent}
                                   checked={this.state.search_content}
                                   aria-label="Search content" />
                        </span>
                        <input type="text" className="form-control"
                               onChange={this.setQuery}
                               placeholder="Search text" />
                    </div>
                    </form>
                </Row>
        );
    },
    setQuery: function(evnt) {
        this.setState({query: evnt.target.value});
    },
    toogleSTitle: function() {
        this.setState({search_title: !this.state.search_title},
                      this.launchSearch);
    },
    toogleSContent: function() {
        this.setState({search_content: !this.state.search_content},
                      this.launchSearch);
    },
    launchSearch: function(evnt) {
        if(this.state.query && (this.state.search_title
                             || this.state.search_content)) {
            MiddlePanelActions.search({query: this.state.query,
                                       title: this.state.search_title,
                                       content: this.state.search_content});
        }
        if(evnt) {
            evnt.preventDefault();
        }
    },
});

var MiddlePanelFilter = React.createClass({
    getInitialState: function() {
        return {filter: MiddlePanelStore._datas.filter,
                display_search: MiddlePanelStore._datas.display_search};
    },
    render: function() {
        var search_row = null;
        if(this.state.display_search) {
            search_row = <MiddlePanelSearchRow />
        }
        return (<div>
                <Row className="show-grid">
                    <ButtonGroup>
                        <Button active={this.state.filter == "all"}
                                onMouseDown={this.setAllFilter}
                                bsSize="small">All</Button>
                        <Button active={this.state.filter == "unread"}
                                onMouseDown={this.setUnreadFilter}
                                bsSize="small">Unread</Button>
                        <Button active={this.state.filter == "liked"}
                                onMouseDown={this.setLikedFilter}
                                bsSize="small">
                            <Glyphicon glyph="star" />
                        </Button>
                    </ButtonGroup>
                    <ButtonGroup>
                        <Button onMouseDown={this.toogleSearch} bsSize="small">
                            <Glyphicon glyph="search" />
                        </Button>
                    </ButtonGroup>
                    <ButtonGroup>
                        <Button onMouseDown={MiddlePanelActions.markAllAsRead}
                                bsSize="small">Mark all as read</Button>
                    </ButtonGroup>
                </Row>
                {search_row}
                </div>
        );
    },
    setAllFilter: function() {
        this.setState({filter: 'all'});
        MiddlePanelActions.setFilter('all');
    },
    setUnreadFilter: function() {
        this.setState({filter: 'unread'});
        MiddlePanelActions.setFilter('unread');
    },
    setLikedFilter: function() {
        this.setState({filter: 'liked'});
        MiddlePanelActions.setFilter('liked');
    },
    toogleSearch: function() {
        if(this.state.display_search) {
            MiddlePanelActions.search_off();
        }
        this.setState({display_search: !this.state.display_search});
    },
});

var MiddlePanel = React.createClass({
    getInitialState: function() {
        return {filter: MiddlePanelStore._datas.filter, articles: []};
    },
    render: function() {
        return (<Row className="show-grid">
                    <div className="list-group">
                    {this.state.articles.map(function(article){
                        return (<TableLine key={"a" + article.article_id}
                                        title={article.title}
                                        icon_url={article.icon_url}
                                        read={article.read}
                                        liked={article.liked}
                                        date={article.date}
                                        article_id={article.article_id}
                                        feed_id={article.feed_id}
                                        category_id={article.category_id}
                                        feed_title={article.feed_title} />);})}
                    </div>
                </Row>
        );
    },
    componentDidMount: function() {
        MiddlePanelActions.reload();
        MiddlePanelStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        MiddlePanelStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        this.setState({filter: MiddlePanelStore._datas.filter,
                       articles: MiddlePanelStore.getArticles()});
    },
});

module.exports = {MiddlePanel: MiddlePanel,
                  MiddlePanelFilter: MiddlePanelFilter};
