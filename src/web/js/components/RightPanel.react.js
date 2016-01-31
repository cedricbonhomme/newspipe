var React = require('react');
var Col = require('react-bootstrap/lib/Col');
var Glyphicon = require('react-bootstrap/lib/Glyphicon');
var Button = require('react-bootstrap/lib/Button');
var ButtonGroup = require('react-bootstrap/lib/ButtonGroup');

var RightPanelActions = require('../actions/RightPanelActions');
var RightPanelStore = require('../stores/RightPanelStore');
var JarrTime = require('./time.react');

var PanelMixin = {
    propTypes: {obj: React.PropTypes.object.isRequired},
    getInitialState: function() {
        return {edit_mode: false, obj: this.props.obj};
    },
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
        this.fields.filter(function(field) {
            return field.type != 'ignore';
        }).map(function(field) {
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
        items.push(<dd key={this.getKey('dd', 'submit')}>
                        <button className="btn btn-default"
                                onClick={this.saveObj}>
                            Submit
                        </button>
                    </dd>);
        this.fields.filter(function(field) {
            return field.type != 'ignore';
        }).map(function(field) {
            key = this.getKey('dd', field.key);
            items.push(<dt key={key}>{field.title}</dt>);
            key = this.getKey('dt', field.key);
            var input = null;
            if(field.type == 'string' || field.type == 'link') {
                input = (<input type="text" name={field.key}
                                onChange={this.saveField}
                                defaultValue={this.props.obj[field.key]} />);
            } else if (field.type == 'bool') {
                input = (<input type="checkbox" name={field.key}
                                onChange={this.saveField}
                                defaultChecked={this.props.obj[field.key]} />);
            }
            items.push(<dd key={key}>{input}</dd>);
        }.bind(this));
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
        RightPanelActions.delObj(this.props.obj.id, this.obj_type);
    },
    saveField: function(evnt) {
        var obj = this.state.obj;
        for(var i in this.fields) {
            if(evnt.target.name == this.fields[i].key) {
                if(this.fields[i].type == 'bool') {
                    obj[evnt.target.name] = evnt.target.checked;
                } else {
                    obj[evnt.target.name] = evnt.target.value;
                }
                break;
            }
        }
        this.setState({obj: obj});
    },
    saveObj: function() {
        var to_push = {};
        this.fields.map(function(field) {
            to_push[field.key] = this.state.obj[field.key];
        }.bind(this));
        this.setState({edit_mode: false}, function() {
            RightPanelActions.putObj(this.props.obj.id, this.obj_type, to_push);
        }.bind(this));
    },
};

var Article = React.createClass({
    mixins: [PanelMixin],
    isEditable: function() {return false;},
    isRemovable: function() {return true;},
    fields: [],
    obj_type: 'article',
    getTitle: function() {return this.props.obj.title;},
    getBody: function() {
        return (<div className="panel-body" dangerouslySetInnerHTML={
                        {__html: this.props.obj.content}} />);
    },
});

var Feed = React.createClass({
    mixins: [PanelMixin],
    isEditable: function() {return true;},
    isRemovable: function() {return true;},
    obj_type: 'feed',
    fields: [{'title': 'Feed title', 'type': 'string', 'key': 'title'},
             {'title': 'Description', 'type': 'string', 'key': 'description'},
             {'title': 'Feed link', 'type': 'link', 'key': 'link'},
             {'title': 'Site link', 'type': 'link', 'key': 'site_link'},
             {'title': 'Enabled', 'type': 'bool', 'key': 'enabled'},
             {'title': 'Filters', 'type': 'ignore', 'key': 'filters'},
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
                <select name="action on" className="form-control"
                        data-index={i} onChange={this.saveFilterChange}
                        defaultValue={filter['action on']}>
                    <option value="match">match</option>
                    <option value="no match">no match</option>
                </select>
                <input name="pattern" type="text" className="form-control"
                        data-index={i} onChange={this.saveFilterChange}
                        defaultValue={filter.pattern} />
                <select name="type" className="form-control"
                        data-index={i} onChange={this.saveFilterChange}
                        defaultValue={filter.type}>
                    <option value='simple match'>simple match</option>
                    <option value='regex'>regex</option>
                </select>
                <select name="action" className="form-control"
                        data-index={i} onChange={this.saveFilterChange}
                        defaultValue={filter.action}>
                    <option value="mark as read">mark as read</option>
                    <option value="mark as favorite">mark as favorite</option>
                </select>
            </dd>);
    },
    getFilterRows: function() {
        var rows = [];
        if(this.state.edit_mode) {
            for(var i in this.state.obj.filters) {
                rows.push(this.getFilterRow(i, this.state.obj.filters[i]));
            }
            return (<dl className="dl-horizontal">
                        <dt>Filters</dt>
                        <dd>
                            <button className="btn btn-default"
                                    type="button" onClick={this.addFilterRow}>
                                <Glyphicon glyph='plus' />
                            </button>
                        </dd>
                        {rows}
                    </dl>);
        }
        rows = [];
        rows.push(<dt key={'d-title'}>Filters</dt>);
        for(var i in this.state.obj.filters) {
            rows.push(<dd key={'d' + i}>
                    When {this.state.obj.filters[i]['action on']} on "{this.state.obj.filters[i].pattern}" ({this.state.obj.filters[i].type}) => {this.state.obj.filters[i].action}
                    </dd>);
        }
        return <dl className="dl-horizontal">{rows}</dl>;
    },
    getBody: function() {
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
                    {this.getFilterRows()}
                </div>
        );
    },
    addFilterRow: function() {
        var obj = this.state.obj;
        obj.filters.push({action: "mark as read", 'action on': "match",
                      type: "simple match", pattern: ""});
        this.setState({obj: obj});
    },
    removeFilterRow: function(evnt) {
        var obj = this.state.obj;
        delete obj.filters[evnt.target.getAttribute('data-index')];
        this.setState({obj: obj});
    },
    saveFilterChange: function(evnt) {
        var index = evnt.target.getAttribute('data-index');
        var obj = this.state.obj;
        obj.filters[index][evnt.target.name] = evnt.target.value;
        this.setState({obj: obj});
    },
});

var Category = React.createClass({
    mixins: [PanelMixin],
    isEditable: function() {
        if(this.props.obj.id != 0) {return true;}
        else {return false;}
    },
    isRemovable: function() {return this.isEditable();},
    obj_type: 'category',
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
        window.scrollTo(0, 0);
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

        return (<Col id="right-panel" xsOffset={4} smOffset={4}
                                      mdOffset={7} lgOffset={6}
                                      xs={8} sm={8} md={5} lg={6}>
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
        this.setState(RightPanelStore.getAll());
    },
});

module.exports = RightPanel;
