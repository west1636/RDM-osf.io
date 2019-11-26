<%namespace name="contributor_list" file="../util/contributor_list.mako" />
<div id="projectScope">
    <header class="subhead" id="overview">

        <div id="title" class="row">
            <h2 class="node-title">
                <span id="nodeTitle" class="overflow">${ node['title'] }</span>
            </h2>
        </div>

        <div id="contributors" class="row" style="line-height:25px">
            <div class="col-sm-12">
                ${ _("Contributors:") }
                % if node['anonymous'] and not node['is_public']:
                    <ol>${ _("Anonymous Contributors") }</ol>
                % else:
                    <ol>
                        ${contributor_list.render_contributors_full(contributors=node['contributors'])}
                    </ol>
                % endif
                % if node['is_fork']:
                    <br />${ _('Forked from <a class="node-forked-from" href="%(forkedfromid)s">%(forkedfromdiplay)s</a> on\
                    <span data-bind="text: dateForked.local, tooltip: {title: dateForked.utc}"></span>',forkedfromid=node['forked_from_id'],forkedfromdiplay=node['forked_from_display_absolute_url']) }
                % endif
                <p>
                  Registration Form:
                  % for meta_schema in node.get('registered_schemas', []):
                  <span> ${meta_schema['schema_name']}</span>
                  % if len(node['registered_schemas']) > 1:
                  ,
                  % endif
                  % endfor
                </p>
                <br />
                ${ _("Date Created:") }
                <span data-bind="text: dateCreated.local, tooltip: {title: dateCreated.utc}" class="date node-date-created"></span>
                <br/>
                ${ _("Date Registered:") }
                <span data-bind="text: dateRegistered.local, tooltip: {title: dateRegistered.utc}" class="date node-date-registered"></span>
                <br/>
                ${ _("Date Withdrawn:") }
                % if node['date_retracted']:
                    <span data-bind="text: dateRetracted.local, tooltip: {title: dateRetracted.utc}" class="date node-date-retracted"></span>
                % else:
                    ${ _("Not available") }
                % endif
                <span data-bind="if: hasDoi()" class="scripted">
                  <p>
                    <span data-bind="text:identifier"></span>:
                  DOI <span data-bind="text: doi"></span>
                      <span data-bind="if: hasArk()" class="scripted">| ARK <span data-bind="text: ark"></span></span>
                   </p>
                </span>

                % if parent_node['id']:
                    <br />${ _("Category: ") }<span class="node-category">${ node['category'] }</span>
                % elif node['description'] or permissions.WRITE in user['permissions']:
                    <br /><span id="description">Description:</span> <span id="nodeDescriptionEditable" class="node-description overflow" data-type="textarea">${ node['description'] }</span>
                % endif
            </div>
        </div>

        <div id="justification" class="row">
            <div class="col-sm-6">
                <div id="justificationWidget" class="addon-widget-container">
                    <div class="addon-widget" name="justification">
                        <div class="addon-widget-header clearfix">
                            <h4>${ _("Justification for Withdrawal") }</h4>
                        </div>
                        <div class="addon-widget-body">
                            % if not node['retracted_justification']:
                                <em>${ _("No justification provided during withdrawal.") }</em>
                            % else:
                                ${ node['retracted_justification'] }
                            % endif
                        </div>
                    </div>
                </div>
            </div>
        </div>

    </header>
</div>
