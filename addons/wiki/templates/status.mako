% for i, breadcrumb in enumerate(breadcrumbs_list):
    % if breadcrumb:
        % if i > 0:
            /
        % endif
        <a href="${urls['web']['home']}/${"/".join(breadcrumbs_list[i:i+1])}/">${breadcrumb}</a>
    % endif
% endfor

<h3 class="wiki-title wiki-title-xs" id="wikiName">
    % if wiki_name == 'home':
        <i class="fa fa-home"></i>
    % endif
    <span id="pageName"
        % if wiki_name == 'home' and not node['is_registration']:
            data-bind="tooltip: {title: '${_("Note: Home page cannot be renamed.")}'}"
        % endif
    >${wiki_name if wiki_name != 'home' else _("Home")}</span>
</h3>
