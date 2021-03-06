'use strict';
var lodashGet  = require('lodash.get');

var _ = require('js/rdmGettext')._;

/**
 * Helper for required options passed to components.
 * Usage:
 *    var title = required(opts, 'title')
 *    var lastName = required(opts, 'name.last')
 */
function required(opts, attribute) {
    var opt = lodashGet(opts, attribute);
    if (opt == null || opt === undefined) {
        throw new Error(_('Missing required option: ') + attribute);
    }
    return opt;
}

module.exports = {
    required: required
};
