/*
 * Copyright (c) 2014-2015, Facebook, Inc.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree. An additional grant
 * of patent rights can be found in the PATENTS file in the same directory.
 *
 * TodoConstants
 */

var keyMirror = require('keymirror');

module.exports = {
    MenuActionTypes: keyMirror({
        RELOAD_MENU: null,
        MENU_FILTER_ALL: null,
        MENU_FILTER_UNREAD: null,
        MENU_FILTER_ERROR: null,
    }),
    MiddlePanelActionTypes: keyMirror({
        RELOAD_MIDDLE_PANEL: null,
        MIDDLE_PANEL_PARENT_FILTER: null,
        MIDDLE_PANEL_FILTER_ALL: null,
        MIDDLE_PANEL_FILTER_UNREAD: null,
        MIDDLE_PANEL_FILTER_LIKED: null,
    }),
};
