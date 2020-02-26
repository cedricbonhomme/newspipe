var React = require('react');
var createReactClass = require('create-react-class');

var Row = require('react-bootstrap/lib/Row');
var Button = require('react-bootstrap/lib/Button');
var ButtonGroup = require('react-bootstrap/lib/ButtonGroup');
var Glyphicon = require('react-bootstrap/lib/Glyphicon');
var PropTypes = require('prop-types');

var MiddlePanelStore = require('../stores/MiddlePanelStore');
var MiddlePanelActions = require('../actions/MiddlePanelActions');
var RightPanelActions = require('../actions/RightPanelActions');

var JarrTime = require('./time.react');

var TableLine = createReactClass({
    propTypes: {article_id: PropTypes.number.isRequired,
                feed_title: PropTypes.string.isRequired,
                icon_url: PropTypes.string,
                title: PropTypes.string.isRequired,
                rel_date: PropTypes.string.isRequired,
                date: PropTypes.string.isRequired,
                read: PropTypes.bool.isRequired,
                selected: PropTypes.bool.isRequired,
                liked: PropTypes.bool.isRequired,
    },
    getInitialState: function() {
        return {read: this.props.read, liked: this.props.liked,
                selected: false};
    },
    render: function() {
        var liked = this.state.liked ? 'l' : '';
        var icon = null;
        if(this.props.icon_url){
            icon = (<img width="16px" src={this.props.icon_url} />);
        } else {
            icon = <Glyphicon glyph="ban-circle" />;
        }
        var title = (<a href={'/article/redirect/' + this.props.article_id}
                        onClick={this.openRedirectLink} target="_blank"
                        title={this.props.feed_title}>
                        {icon} {this.props.feed_title}
                     </a>);
        var read = (<Glyphicon glyph={this.state.read?"check":"unchecked"}
                               onClick={this.toogleRead} />);
        var liked = (<Glyphicon glyph={this.state.liked?"star":"star-empty"}
                                onClick={this.toogleLike} />);
        icon = <Glyphicon glyph={"new-window"} />;
        var clsses = "list-group-item";
        if(this.props.selected) {
            clsses += " active";
        }
        return (<div className={clsses} onClick={this.loadArticle} title={this.props.title}>
                    <h5><strong>{title}</strong></h5>
                    <JarrTime text={this.props.date}
                              stamp={this.props.rel_date} />
                    <div>{read} {liked} {this.props.title}</div>
                </div>
        );
    },
    openRedirectLink: function(evnt) {
        if(!this.state.read) {
            this.toogleRead(evnt);
        }
    },
    toogleRead: function(evnt) {
        this.setState({read: !this.state.read}, function() {
            MiddlePanelActions.changeRead(this.props.category_id,
                    this.props.feed_id, this.props.article_id, this.state.read);
        }.bind(this));
        evnt.stopPropagation();
    },
    toogleLike: function(evnt) {
        this.setState({liked: !this.state.liked}, function() {
            MiddlePanelActions.changeLike(this.props.category_id,
                    this.props.feed_id, this.props.article_id, this.state.liked);
        }.bind(this));
        evnt.stopPropagation();
    },
    loadArticle: function() {
        this.setState({selected: true, read: true}, function() {
            RightPanelActions.loadArticle(
                    this.props.article_id, this.props.read);
        }.bind(this));
    },
    stopPropagation: function(evnt) {
        evnt.stopPropagation();
    },
});

var MiddlePanelSearchRow = createReactClass({
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

var MiddlePanelFilter = createReactClass({
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
                                title="Display all articles"
                                onClick={this.setAllFilter} bsSize="small">
                            <Glyphicon glyph="menu-hamburger" />
                        </Button>
                        <Button active={this.state.filter == "unread"}
                                title="Display only unread article"
                                onClick={this.setUnreadFilter}
                                bsSize="small">
                            <Glyphicon glyph="unchecked" />
                        </Button>
                        <Button active={this.state.filter == "liked"}
                                title="Filter only liked articles"
                                onClick={this.setLikedFilter}
                                bsSize="small">
                            <Glyphicon glyph="star" />
                        </Button>
                    </ButtonGroup>
                    <ButtonGroup>
                        <Button onClick={this.toogleSearch}
                                title="Search through displayed articles"
                                bsSize="small">
                            <Glyphicon glyph="search" />
                        </Button>
                    </ButtonGroup>
                    <ButtonGroup>
                        <Button onClick={MiddlePanelActions.markAllAsRead}
                                title="Mark all displayed article as read"
                                bsSize="small">
                            <Glyphicon glyph="trash" />
                        </Button>
                    </ButtonGroup>
                </Row>
                {search_row}
                </div>
        );
    },
    setAllFilter: function() {
        this.setState({filter: 'all'}, function() {
            MiddlePanelActions.setFilter('all');
        }.bind(this));
    },
    setUnreadFilter: function() {
        this.setState({filter: 'unread'}, function() {
            MiddlePanelActions.setFilter('unread');
        }.bind(this));
    },
    setLikedFilter: function() {
        this.setState({filter: 'liked'}, function() {
            MiddlePanelActions.setFilter('liked');
        }.bind(this));
    },
    toogleSearch: function() {
        this.setState({display_search: !this.state.display_search},
            function() {
                if(!this.state.display_search) {
                    MiddlePanelActions.search_off();
                }
            }.bind(this)
        );
    },
});

var MiddlePanel = createReactClass({
    getInitialState: function() {
        return {filter: MiddlePanelStore._datas.filter, articles: []};
    },
    render: function() {
        return (<Row className="show-grid">
                    <div className="list-group">
                    {this.state.articles.map(function(article){
                        var key = "a" + article.article_id;
                        if(article.read) {key+="r";}
                        if(article.liked) {key+="l";}
                        if(article.selected) {key+="s";}
                        return (<TableLine key={key}
                                        title={article.title}
                                        icon_url={article.icon_url}
                                        read={article.read}
                                        liked={article.liked}
                                        rel_date={article.rel_date}
                                        date={article.date}
                                        selected={article.selected}
                                        article_id={article.article_id}
                                        feed_id={article.feed_id}
                                        locales={['en']}
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
