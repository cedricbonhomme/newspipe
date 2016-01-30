var React = require('react');
var Col = require('react-bootstrap/Col');
var Glyphicon = require('react-bootstrap/Glyphicon');
var Button = require('react-bootstrap/Button');
var ButtonGroup = require('react-bootstrap/ButtonGroup');

var RightPanelStore = require('../stores/RightPanelStore');
var JarrTime = require('./time.react');

var PanelMixin = {
    propTypes: {obj: React.PropTypes.object.isRequired},
    getHeader: function() {
        var icon = null;
        if(this.props.obj.icon_url){
            icon = (<img width="16px" src={this.props.obj.icon_url} />);
        }
        var btn_grp = null;
        if(this.isEditable() || this.isRemovable()) {
            var edit_button = null;
            if(this.isEditable()) {
                edit_button = (<Button onClick={this.onClickEdit}>
                                <Glyphicon glyph="pencil" />
                               </Button>);
            }
            var rem_button = null;
            if(this.isRemovable()) {
                rem_button = (<Button onClick={this.onClickRemove}>
                                <Glyphicon glyph="remove-sign" />
                              </Button>);
            }
            btn_grp = (<ButtonGroup bsSize="small">
                           {edit_button}
                           {rem_button}
                       </ButtonGroup>);
        }
        return (<div id="right-panel-heading" className="panel-heading">
                    <h4>{icon}<strong>Title:</strong> {this.getTitle()}</h4>
                    {btn_grp}
               </div>);
    },
    getKey: function(prefix, suffix) {
        return ((this.state.edit_mode?'edit':'fix') + prefix
                + '-' + this.props.obj.id + '-' + suffix);
    },
    getCore: function() {
        var items = [];
        var key;
        if(!this.state.edit_mode) {
        this.fields.map(function(field) {
            key = this.getKey('dt', field.key);
            items.push(<dt key={key}>{field.title}</dt>);
            key = this.getKey('dd', field.key);
            if(field.type == 'string') {
                items.push(<dd key={key}>{this.props.obj[field.key]}</dd>);
            } else if(field.type == 'bool') {
                if(this.props.obj[field.key]) {
                    items.push(<dd key={key}><Glyphicon glyph="ok" /></dd>);
                } else {
                    items.push(<dd key={key}><Glyphicon glyph="pause" /></dd>);
                }
            } else if (field.type == 'link') {
                items.push(<dd key={key}>
                              <a href={this.props.obj[field.key]}>
                            {this.props.obj[field.key]}
                              </a>
                           </dd>);
            }
        }.bind(this));
        } else {
        this.fields.map(function(field) {
            key = this.getKey('dd', field.key);
            items.push(<dt key={key}>{field.title}</dt>);
            key = this.getKey('dt', field.key);
            if(field.type == 'string' || field.type == 'link') {
                items.push(<dd key={key}><input type="text"
                                    defaultValue={this.props.obj[field.key]} />
                           </dd>);
            } else if (field.type == 'bool') {
                items.push(<dd key={key}><input type="checkbox"
                           defaultChecked={this.props.obj[field.key]} /></dd>);
            }
        }.bind(this));
            items.push(<dd key={this.getKey('dd', 'submit')}>
                           <button className="btn btn-default">
                               Submit
                           </button>
                       </dd>);
        }
        return (<dl className="dl-horizontal">{items}</dl>);
    },
    render: function() {
        return (<div className="panel panel-default">
                    {this.getHeader()}
                    {this.getBody()}
                </div>
        );
    },
    onClickEdit: function() {
        this.setState({edit_mode: !this.state.edit_mode});
    },
    onClickRemove: function() {
    },
};

var Article = React.createClass({
    mixins: [PanelMixin],
    getInitialState: function() {return {edit_mode: false};},
    fields: [],
    isEditable: function() {return false;},
    isRemovable: function() {return true;},
    getTitle: function() {return this.props.obj.title;},
    getBody: function() {
        return (<div className="panel-body" dangerouslySetInnerHTML={
                        {__html: this.props.obj.content}} />);
    },
});

var Feed = React.createClass({
    mixins: [PanelMixin],
    getInitialState: function() {
        return {edit_mode: false, filters: this.props.obj.filters};
    },
    isEditable: function() {return true;},
    isRemovable: function() {return true;},
    fields: [{'title': 'Feed title', 'type': 'string', 'key': 'title'},
             {'title': 'Description', 'type': 'string', 'key': 'description'},
             {'title': 'Feed link', 'type': 'link', 'key': 'link'},
             {'title': 'Site link', 'type': 'link', 'key': 'site_link'},
             {'title': 'Enabled', 'type': 'bool', 'key': 'enabled'},
    ],
    getTitle: function() {return this.props.obj.title;},
    getFilterRow: function(i, filter) {
        return (<dd key={'d' + i + '-' + this.props.obj.id}
                        className="input-group filter-row">
                <span className="input-group-btn">
                    <button className="btn btn-default" type="button"
                            data-index={i} onClick={this.removeFilterRow}>
                        <Glyphicon glyph='minus' />
                    </button>
                </span>
                <select name="type" className="form-control"
                        defaultValue={filter.type}>
                    <option value='simple match'>simple match</option>
                    <option value='regex'>regex</option>
                </select>
                <input type="text" className="form-control"
                        name="pattern" defaultValue={filter.pattern} />
                <select name="action_on" className="form-control"
                        defaultValue={filter.action_on}>
                    <option value="match">match</option>
                    <option value="no match">no match</option>
                </select>
                <select name="action" className="form-control"
                        defaultValue={filter.action}>
                    <option value="mark as read">mark as read</option>
                    <option value="mark as favorite">mark as favorite</option>
                </select>
            </dd>);
    },
    getBody: function() {
        var filter_rows = [];
        for(var i in this.state.filters) {
            filter_rows.push(this.getFilterRow(i, this.state.filters[i]));
        }
        return (<div className="panel-body">
                    <dl className="dl-horizontal">
                        <dt>Created on</dt>
                        <dd><JarrTime stamp={this.props.obj.created_stamp}
                                      text={this.props.obj.created_date} />
                        </dd>
                        <dt>Last fetched</dt>
                        <dd><JarrTime stamp={this.props.obj.last_stamp}
                                      text={this.props.obj.last_retrieved} />
                        </dd>
                    </dl>
                    {this.getCore()}
                    <dl className="dl-horizontal">
                    <form>
                        <dt>Filters</dt>
                        <dd>
                            <button className="btn btn-default"
                                    type="button" onClick={this.addFilterRow}>
                                <Glyphicon glyph='plus' />
                            </button>
                            <button className="btn btn-default">Submit
                            </button>
                        </dd>
                        {filter_rows}
                    </form>
                    </dl>
                </div>
        );
    },
    addFilterRow: function() {
        var filters = this.state.filters;
        filters.push({action: null, action_on: null,
                      type: null, pattern: null});
        this.setState({filters: filters});
    },
    removeFilterRow: function(evnt) {
        var filters = this.state.filters;
        delete filters[evnt.target.getAttribute('data-index')];
        this.setState({filters: filters});
    },
});

var Category = React.createClass({
    mixins: [PanelMixin],
    getInitialState: function() {return {edit_mode: false};},
    isEditable: function() {
        if(this.props.obj.id != 0) {return true;}
        else {return false;}
    },
    isRemovable: function() {return this.isEditable();},
    fields: [{'title': 'Category name', 'type': 'string', 'key': 'name'}],
    getTitle: function() {return this.props.obj.name;},
    getBody: function() {
        return (<div className="panel-body">
                    {this.getCore()}
                </div>);
    },
});

var RightPanel = React.createClass({
    getInitialState: function() {
        return {category: null, feed: null, article: null, current: null};
    },
    getCategoryCrum: function() {
        return (<li><a onClick={this.selectCategory} href="#">
                    {this.state.category.name}
                </a></li>);
    },
    getFeedCrum: function() {
        return (<li><a onClick={this.selectFeed} href="#">
                    {this.state.feed.title}
                </a></li>);
    },
    getArticleCrum: function() {
        return <li>{this.state.article.title}</li>;
    },
    render: function() {
        var content = null;
        var brd_category = null;
        var brd_feed = null;
        var brd_article = null;
        var breadcrum = null;
        if(this.state.category) {
            brd_category = (<li><a onClick={this.selectCategory} href="#">
                                {this.state.category.name}
                            </a></li>);
        }
        if(this.state.feed) {
            brd_feed = (<li><a onClick={this.selectFeed} href="#">
                            {this.state.feed.title}
                        </a></li>);
        }
        if(this.state.article) {
            brd_article = <li>{this.state.article.title}</li>;
        }
        if(brd_category || brd_feed || brd_article) {
            breadcrum = (<ol className="breadcrumb">
                            {brd_category}
                            {brd_feed}
                            {brd_article}
                         </ol>);
        }
        if(this.state.current == 'article') {
            var cntnt = (<Article type='article' obj={this.state.article}
                    key={this.state.article.id} />);
        } else if(this.state.current == 'feed') {
            var cntnt = (<Feed type='feed' obj={this.state.feed}
                    key={this.state.feed.id} />);
        } else if(this.state.current == 'category') {
            var cntnt = (<Category type='category' obj={this.state.category}
                    key={this.state.category.id} />);
        }

        return (<Col id="right-panel" xsOffset={2} smOffset={2}
                                      mdOffset={7} lgOffset={6}
                                      xs={10} sm={10} md={5} lg={6}>
                    {breadcrum}
                    {cntnt}
                </Col>
        );
    },
    selectCategory: function() {
        this.setState({current: 'category'});
    },
    selectFeed: function() {
        this.setState({current: 'feed'});
    },
    selectArticle: function() {
        this.setState({current: 'article'});
    },
    componentDidMount: function() {
        RightPanelStore.addChangeListener(this._onChange);
    },
    componentWillUnmount: function() {
        RightPanelStore.removeChangeListener(this._onChange);
    },
    _onChange: function() {
        this.setState(RightPanelStore._datas);
    },
});

module.exports = RightPanel;
