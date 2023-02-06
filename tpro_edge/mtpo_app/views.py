import colorsys
import os
import random
from datetime import datetime, timedelta
import glob

import pandas as pd
import plotly.graph_objs as go
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
# Create your views here.
from django.template.loader import get_template
from django.views import View
# from mtpo_app.formatter import ToSystem
from mtpo_app.models import Site, Reading
from markupsafe import Markup
from plotly.offline import plot

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', -1)
pd.set_option('display.float_format', lambda x: '%.2f' % x)


def get_rgb():
    h, s, l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
    r, g, b = [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]
    return 'rgb(%d,%d,%d)' % (r, g, b)


class Dashboard(View):

    def get(self, request):
        # try:
            #2021 06 01 12_Dibrugarh
            # SOURCE_DIR = r'/home/ittpl/Desktop/WRD Chattisgarh Data 20.01.2023 to 25.01.2023'
            # cwc_files = os.listdir(SOURCE_DIR)
            # print(cwc_files,'files')
            # for f in cwc_files:
                # print("filesname", f)
                # if f.endswith('.csv'):
                    # fname = os.path.join(settings.SOURCE_DIR, f)
                    # addfile = ToSystem(fpath=fname)
                    # addfile.add2db()
            # list_of_files = glob.glob(SOURCE_DIR)# * means all if need specific format then *.csv
            # file_type = '\*amp'
            # files = glob.glob(SOURCE_DIR + file_type)
            # filename = max(files, key=os.path.getctime)
            #filename = max(list_of_files, key=int(os.path.getctime(r'D:\FTP_Raw\Jaipur_Raw')))
            # print(filename,"i am the latest file ")
            #filename = datetime.now().strftime('%Y%m%d%H.amp')
            # filename = os.path.join(settings.SOURCE_DIR, filename)
            # addfile = ToSystem(fpath=filename)
            # print('Updating Database %s' % filename)
            # addfile.add2db()
        # except IndexError: #Exception as e:
        #     print(str(e))
        #     pass
        # try:
        #     site = Site.objects.get(prefix=settings.PREFIX)
        #     content = {'station': site}
        #     graph_details = render_chart(site=site)
        #     content.update(**graph_details)
        # except Site.DoesNotExist:
        # except:
        content = {}
        sites = Site.objects.all().order_by('name')
        for i in sites:
            try:
                i.last_dict_reading = eval(i.last_reading)
            except:
                i.last_dict_reading = {'d' : 's'}
        content['sites'] = sites
        content['live'] = Site.objects.filter(status='Live')
        content['delay'] = Site.objects.filter(status='Delay')
        content['offline'] = Site.objects.filter(status='Offline')
        info_template = get_template('dashboard.html')
        html = info_template.render(content, request)
        return HttpResponse(html)


class Reports(View):

    def get(self, request):
        # assuming we will have only one station
        try:
            site = Site.objects.get(prefix=settings.PREFIX)
            content = {'station': site}
            graph_details = render_chart(site=site)
            content.update(**graph_details)
        except Site.DoesNotExist:
            content = {'config_required': True}
        info_template = get_template('reporting.html')
        html = info_template.render(content, request)
        return HttpResponse(html)


def render_chart(**kwargs):
    site = kwargs.get('site')
    print(site)
    from_date = kwargs.get('from_date')
    to_date = kwargs.get('to_date')
    if not (from_date and to_date):
        to_date = datetime.now()
        from_date = to_date - timedelta(days=30)
    else:
        from_date = datetime.strptime(from_date, "%m/%d/%Y %H:%M")
        to_date = datetime.strptime(to_date, "%m/%d/%Y %H:%M")
    # status = site.status
    # if status.lower() == 'live':
    #     status = 'success', 'Live'
    # elif status.lower() == 'delay':
    #     status = 'warning', 'Delay',
    # else:
    #     status = 'danger', 'Offline'
    details = {
        'id': site.id,
        'reload_time': 5 * 60 * 1000,  # 5 minutes
        'name': site.name.replace('_', ' ').title(),
        # 'status': status,
        'industry': site.industry,
        'from': from_date.strftime("%m/%d/%Y %H:%M"),
        'to': to_date.strftime("%m/%d/%Y %H:%M"),
    }
    q = {
        'reading__timestamp__gte': from_date,
        'reading__timestamp__lte': to_date,
    }
    readings = Reading.objects.filter(site=site, **q).values_list('reading',
                                                                  flat=True)
    df = pd.DataFrame(readings)
    if not df.empty:
        cols = df.columns.drop('timestamp')
        df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        df.sort_index(ascending=True, inplace=True)
    xaxis = dict(showgrid=True, title_text='Time', linecolor='grey')
    yaxis = dict(showgrid=True, title_text='Parameter Value', linecolor='grey')
    layout = dict(autosize=True,
                  paper_bgcolor='white', plot_bgcolor='white',
                  xaxis=xaxis, yaxis=yaxis, title=site.name,
                  title_x=0.5,
                  xaxis_showgrid=True,
                  yaxis_showgrid=True
                  )

    obj_layout = go.Figure(layout=layout)
    js_layout = layout
    cards = {}
    # threshld_shapes = []
    traces = []  # parameter lines
    for param in list(df.columns):
        if param != 'timestamp':
            df[param] = pd.to_numeric(df[param], errors='coerce',
                                      downcast="float")
            tmp_df = df[param].sort_index(ascending=False)
            if not tmp_df.empty:
                lastest_rec = tmp_df.head(1).to_dict()
                ltimestamp, lvalue = list(lastest_rec.keys())[0], \
                                     list(lastest_rec.values())[0]
                lvalue = "{:.2f}".format(lvalue)
            else:
                ltimestamp = lvalue = ''
            if ltimestamp:
                try:
                    ltimestamp = ltimestamp.strftime("%m-%d-%Y %H:%M:00")
                except Exception as er:print(er)
            sp, _ = SiteParameter.objects.get_or_create(site=site, name=param)
            unit = sp.unit or ''
            clr = sp.color or get_rgb()
            # clr = 'rgb(98,45,188)'
            cards[param] = {
                'unit': unit,
                'color': clr,
                'min': "{:.2f}".format(df[param].min()),
                'max': "{:.2f}".format(df[param].max()),
                'avg': "{:.2f}".format(df[param].mean()),
                'last_received': ltimestamp,
                'last_value': lvalue
            }
            df[param] = df[param].apply(lambda x: 0 if x in ['', ' '] else x)
            df[param] = df[param].astype(float)
            df[param].fillna('', inplace=True)
            legend_name = param
            if unit:
                legend_name = '%s (%s)' % (param, unit)
            trace = dict(type='scatter', mode='lines',
                         x=list(df.index),
                         y=list(df[param]),
                         name=legend_name,
                         text='',
                         line=dict(color=clr, width=2,
                                   dash=random.choice(['solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot'])),
                         textposition='bottom center', line_color=clr,
                         opacity=0.8,
                         textfont=dict(family='sans serif',
                                       size=15, color=clr)
                         )

            traces.append(trace)
            obj_layout.add_trace(trace)
    plot_div = Markup(plot(obj_layout, output_type='div', config={
        'displaylogo': False,
        'modeBarButtonsToRemove': [
            'toggleSpikelines',
            'hoverCompareCartesian',
            'sendDataToCloud',
            'hoverClosestCartesian',
            'hoverCompareCartesian'
        ]
    }))
    if not df.empty:
        df = df.sort_index(ascending=False)
        df.reset_index(level=0, inplace=True)
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime(
            "%d/%m/%Y %H:%M:00")
        df.columns = [get_unit(a, concatenate=True) for a in list(df.columns)]

    else:
        layout.update(
            {
                "layout": {
                    "xaxis": {
                        "visible": False
                    },
                    "yaxis": {
                        "visible": False
                    },
                }
            }
        )
    tabl = df.to_html(classes='table table-bordered ScrollStyle',
                      index=False,
                      justify='center')
    cards = generate_html_cards(cards)
    if kwargs.get('update'):
        context = {
            'layout': js_layout,  # for api req
            'data': traces,  # for api req
            'cards': cards,
            'tabular': tabl,
            'from': from_date.strftime("%d %b %Y %H:%M"),
            'to': to_date.strftime("%d %b %Y %H:%M"),
        }
    else:
        context = {
            'chart': plot_div,
            'details': details,
            'cards': cards,
            'tabular': tabl
        }
    return context

def render_split_chart(**kwargs):
    site = kwargs.get('site')
    from_date = kwargs.get('from_date')
    to_date = kwargs.get('to_date')
    if not (from_date and to_date):
        last_reading = Reading.objects.filter(
            site__prefix=settings.PREFIX).latest('reading')
        to_date = datetime.strptime(last_reading.reading.get('timestamp'),
                                    '%Y-%m-%d %H:%M:%S')
        from_date = to_date - timedelta(hours=72)
    else:
        from_date = datetime.strptime(from_date, "%m/%d/%Y %H:%M")
        to_date = datetime.strptime(to_date, "%m/%d/%Y %H:%M")
    details = {
        'id': site.id,
        'reload_time': 5 * 60 * 1000,  # 5 minutes
        'name': site.name.replace('_', ' ').title(),
        # 'status': status,
        'industry': site.industry,
        'from': from_date.strftime("%m/%d/%Y %H:%M"),
        'to': to_date.strftime("%m/%d/%Y %H:%M"),
    }
    # print(details["name"],"name")
    # print(details["industry"], "industr")
    q = {
        'reading__timestamp__gte': from_date,
        'reading__timestamp__lte': to_date,
    }
    readings = Reading.objects.filter(site=site, **q).values_list('reading',
                                                                  flat=True)
    df = pd.DataFrame(readings)
    if not df.empty:
        cols = df.columns.drop('timestamp')
        df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        df.sort_index(ascending=True, inplace=True)
    total_params = len(df.columns) - 1

    GRID_COL = 3
    if 3 < total_params <= 6:
        GRID_ROW = 2
    elif 6 < total_params <= 9:
        GRID_ROW = 3
    elif 6 < total_params <= 12:
        GRID_ROW = 4
    elif 6 < total_params <= 15:
        GRID_ROW = 5
    else:
        GRID_ROW = 2
    layout = dict(autosize=True,
                  paper_bgcolor='white',
                  plot_bgcolor='white',
                  title=site.name,
                  title_x=0.5,
                  grid={"rows": GRID_ROW,
                        "columns": GRID_COL,
                        "pattern": 'independent',
                        "ygap": 0.5,
                        # "xgap": 0.1,
                        },
                  legend=dict(
                      orientation="h",
                      x=0.5,
                      y=1.5,
                      xanchor='center',
                      yanchor='bottom',
                      title_font_family="Times New Roman",
                      font=dict(
                          family="Courier",
                          size=12,
                          color="black"
                      ),
                      # bgcolor="LightSteelBlue",
                      bordercolor="Black",
                      borderwidth=0.5,
                  )
                  )
    obj_layout = go.Figure(layout=layout)
    js_layout = layout
    cards = {}
    # threshld_shapes = []
    traces = []  # parameter lines
    for cnt, param in enumerate(df.columns):
        if param != 'timestamp':
            df[param] = pd.to_numeric(df[param], errors='coerce',
                                      downcast="float")
            tmp_df = df[param].sort_index(ascending=False)
            if not tmp_df.empty:
                lastest_rec = tmp_df.head(1).to_dict()
                ltimestamp, lvalue = list(lastest_rec.keys())[0], \
                                     list(lastest_rec.values())[0]
                lvalue = "{:.2f}".format(lvalue)
            else:
                ltimestamp = lvalue = ''
            if ltimestamp:
                try:
                    ltimestamp = ltimestamp.strftime("%m-%d-%Y %H:%M:00")
                except Exception as er:print(er)
            sp, _ = SiteParameter.objects.get_or_create(site=site, name=param)
            unit = sp.unit or ''
            clr = sp.color or get_rgb()
            # clr = 'rgb(98,45,188)'
            cards[param] = {
                'unit': unit,
                'color': clr,
                'min': "{:.2f}".format(df[param].min()),
                'max': "{:.2f}".format(df[param].max()),
                'avg': "{:.2f}".format(df[param].mean()),
                'last_received': ltimestamp,
                'last_value': lvalue
            }
            # print(cards,"cards")
            df[param] = df[param].apply(lambda x: 0 if x in ['', ' '] else x)
            df[param] = df[param].astype(float)
            df[param].fillna('', inplace=True)
            legend_name = param
            if unit:
                legend_name = '%s (%s)' % (param, unit)
            trace = dict(type='scatter',
                         mode='lines',
                         x=df.index.tolist(),
                         y=list(df[param]),
                         xaxis='x' + str(cnt + 1),
                         yaxis='y' + str(cnt + 1),
                         name=legend_name,
                         text=list(df[param]),
                         textposition='bottom center',
                         # line_color=clr,
                         opacity=0.8,
                         connectgaps=False,  # to show gap
                         line=dict(color=clr,
                                   width=2,
                                   # dash='dot'
                                   ),
                         textfont=dict(family='sans serif',
                                       size=15, color=clr)
                         )
            traces.append(trace)
            obj_layout.add_trace(trace)
    plot_div = Markup(plot(obj_layout, output_type='div', config={
        'displaylogo': False,
        'modeBarButtonsToRemove': [
            'toggleSpikelines',
            'hoverCompareCartesian',
            'hoverClosestCartesian',
            'hoverCompareCartesian'
            'sendDataToCloud',
            'toImage',
        ]
    }))
    if not df.empty:
        df = df.sort_index(ascending=False)
        df.reset_index(level=0, inplace=True)
        df.columns = [get_unit(a, concatenate=True)
                      for a in
                      list(df.columns)]
    else:
        layout.update(
            {
                "layout": {
                    "xaxis": {
                        "visible": False
                    },
                    "yaxis": {
                        "visible": False
                    },
                }
            }
        )
    tabl = df.to_html(classes='table table-bordered ScrollStyle',
                      index=False,
                      justify='center')
    cards = generate_html_cards(cards)
    if kwargs.get('update'):
        context = {
            'layout': js_layout,  # for api req
            'data': traces,  # for api req
            'cards': cards,
            'tabular': tabl,
            'from': from_date.strftime("%d %b %Y %H:%M"),
            'to': to_date.strftime("%d %b %Y %H:%M"),
        }
    else:
        context = {
            'chart': plot_div,
            'details': details,
            'cards': cards,
            'tabular': tabl
        }
    return context


def render_table(**kwargs):
    site = kwargs.get('site')
    from_date = kwargs.get('from_date')
    to_date = kwargs.get('to_date')
    if not (from_date and to_date):
        last_reading = Reading.objects.latest('reading')
        to_date = datetime.strptime(last_reading.reading.get('timestamp'),
                                    '%Y-%m-%d %H:%M:%S')
        from_date = to_date - timedelta(hours=72)
    else:
        from_date = datetime.strptime(from_date, "%m/%d/%Y %H:%M")
        to_date = datetime.strptime(to_date, "%m/%d/%Y %H:%M")

    q = {
        'reading__timestamp__gte': from_date - timedelta(days=1),
        'reading__timestamp__lte': to_date,
    }
    readings = Reading.objects.filter(site=site, **q).values_list('reading',
                                                                  flat=True)
    df = pd.DataFrame(readings)
    if not df.empty:
        cols = df.columns.drop('timestamp')
        df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime(
        "%d/%m/%Y %H:%M")
        df.set_index('timestamp', inplace=True)
        df.sort_index(ascending=True, inplace=True)
        df = df.sort_index(ascending=False)
        df.reset_index(level=0, inplace=True)
        df.columns = [get_unit(a, concatenate=True)
                      for a in
                      list(df.columns)]

    tabl = df.to_html(classes='table table-bordered ScrollStyle',
                      index=False,
                      justify='center')
    context = {
        'tabular': tabl,
        'from': from_date.strftime("%d %b %Y %H:%M"),
        'to': to_date.strftime("%d %b %Y %H:%M"),
    }
    return context


def generate_html_cards(details):
    html_tx = ''
    PARAM_ORDER = [
        #'LEVEL',
        'VELOCITY',
        'DISCHARGE',
        'TURBIDITY',
        'CONDUCTIVITY',
        'PH',
        'DISSOLVED OXYGEN',
        'TEMPERATURE',
        'BATTERY VOLTAGE',
        'WATER LEVEL'

    ]
    for param in PARAM_ORDER:
        meta = details.get(param)
        if not meta:
            continue
        text_info = 'Time'
        last_value = str(meta.get('last_value'))
        if param.lower().startswith('daily'):
            text_info = 'Today'
            last_value = str(meta.get('last_value'))
            if last_value == 'nan':
                last_value = 'N/A'

        param_meta = dict(param=param.upper(),
                          unit=meta.get('unit', ' '),
                          color=meta.get('color', 'orange'),
                          min=meta.get('min'),
                          max=meta.get('max'),
                          avg=meta.get('avg'),
                          last_received=meta.get('last_received'),
                          last_value=last_value,
                          text_info=text_info
                          )
        # print(param_meta,"sssssssss")
        rec = """
        <div class="col-lg-3 mb-2 small-size-card">
        <div class="card bg-custom-gradient shadow">
            <div class="card-body">
                <div class="head">
                    <center style="color: {color}">{param}<a style="font-size: 18px;">&nbsp;<small>({unit})</small></a></center>
                </div>
                <hr style="border-top: 3px solid {color};">
                <div class="col-12 col-xs-12">
                    <div><center style="font-size: 20px; color:black">{last_value}
                    </center></div>
                    <div><center style="font-size: 15px; color:black">{last_received}</center></div>
                </div>
            </div>
        </div>
    </div>
        """.format(**param_meta)
        html_tx += '\n%s' % rec
    return html_tx


def update_chart_n_table(request):
    pk = request.GET.get('site')
    site = Site.objects.get(id=pk)
    kwargs = {
        'from_date': request.GET.get('from_date'),
        'to_date': request.GET.get('to_date'),
        'site': site,
        'update': True,
    }
    if request.GET.get('tabular'):
        context = render_table(**kwargs)
    elif 'split' in request.GET:
        context = render_split_chart(**kwargs)
    else:
        context = render_chart(**kwargs)
    return JsonResponse(context)


def get_unit(param, concatenate=False):
    params = SiteParameter.objects.filter(site__prefix=settings.PREFIX
                                          ).values(
        'name', 'unit')
    units = {itm.get('name'): itm.get('unit') for itm in params if
             itm.get('unit')}
    unit = units.get(param)
    param = param.upper()
    if unit is None:
        unit = ''
    if concatenate:
        if unit:
            return '%s (%s)' % (param, unit)
        else:
            return param
    return unit

class RefreshDB(View):

    def get(self, request):
        try:
            cwc_files = os.listdir(settings.SOURCE_DIR)
            for f in cwc_files:
                print(f,files)
                if f.endswith('.amp'):
                    try:
                        fname = os.path.join(settings.SOURCE_DIR, f)
                        addfile = ToSystem(fpath=fname)
                        addfile.add2db()
                    except:
                        continue
        except Exception as err:
            pass
        response = redirect('/')
        return response

class RefreshDB2(View):

    def get(self, request):
        try:
            cwc_files = os.listdir(settings.SOURCE_DIR)
            for f in cwc_files:
                if f.endswith('.amp'):
                    fname = os.path.join(settings.SOURCE_DIR, f)
                    addfile = ToSystem(fpath=fname)
                    addfile.add2db()

        except Exception as err:
            pass
        response = redirect('/')
        return response