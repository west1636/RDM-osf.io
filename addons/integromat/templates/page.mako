<%inherit file="project/project_base.mako"/>
<%def name="title()">Integromat - ${node['title']}</%def>
<div id="webInteg" >
    <div class="panel panel-default">
        <div class="panel-heading clearfix">
            <h3 class="panel-title" style="padding-bottom: 5px; padding-top: 5px;">Register Conference</h3>
        </div>
    <div>
        <small class="authorized-by">
            % if has_auth:
                % if not is_registration:
                    <div class="panel-body">
                        <form action="${webhook_url}" method="post">
                            <div class="container-fluid" style="padding: 0px">
                                <div>
                                    <div class="pull-left" style="margin-bottom: 5px">
                                        Start Date <input type="text" id="startConf" placeholder='Start date' size="10" autocomplete="off">
                                    </div>
                                    <div class="pull-left" style="margin-left: 10px; margin-bottom: 5px">
                                        Duration <input type="text" id="durationConf" placeholder='Duration' size="10" autocomplete="off">
                                    </div>
                                </div>
                                <div class="pull-left" style="margin-left: 10px; margin-bottom: 5px">
                                    Topic <input type="text" id="topicConf" placeholder='Topic' size="10" autocomplete="off">
                                </div>
                                <button id="registConf" type="submit" class="btn btn-sm btn-default pull-left" style="margin-left: 10px; margin-bottom: 5px">Register Conference</button>
                                </div>
                            </div>
                        </form>
                    </div>
                % endif
            % else:
                    Please
                    <a href="#integromatCredentialsModal" data-toggle="modal">
                    Connect Account
                    </a>
            % endif
        </small>
    </div>
    </div>
</div>
