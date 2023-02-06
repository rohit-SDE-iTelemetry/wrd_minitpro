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
import xlwt
from xlwt import Workbook

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', -1)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

NHP = {
    "73e0bfda": "CGSWNHP_0001",
    "73e0c798": "SAHGAON_015",
    "73e0c94a": "ARANG_005",
    "73e0d4ee": "HATI_028",
    "73e0da3c": "KASDOL_011",
    "73e0e174": "CGSWNHP_0002",
    "73e0efa6": "NANDGHAT_018",
    "73e0f202": "CGSWNHP_0003",
    "73e0fcd0": "CGSWNHP_0004",
    "73e1007c": "CGSWNHP_0005",
    "cgsw0010": "SARNGPAL_003",
    "73e11dd8": "CGSWNHP_0007",
    "73e12690": "CGSWNHP_0008",
    "73e1130a": "CGSWNHP_0006",
    "73e12842": "CGSWNHP_0009",
    "73e10eae": "73E10EAE",
    "cgsw0011a": "CGSW0011A",
    "cgsw0016": "CGSWNHP_0010",
    "cgsw0017": "CGSWNHP_0011",
    "cgsw0018": "CGSWNHP_0012",
    "cgsw0019": "CGSWNHP_0013",
    "cgsw0020": "CGSWNHP_0014",
    "cgsw0021": "CGSWNHP_0015",
    "cgsw0022": "CGSWNHP_0016",
    "cgsw0023": "CGSWNHP_0017",
    "cgsw0024": "CGSWNHP_0018",
    "cgsw0025": "CGSWNHP_0019",
    "cgsw0026": "CGSWNHP_0020",
    "cgsw0027": "CGSWNHP_0021",
    "cgsw0028": "CGSWNHP_0022",
    "cgsw0029": "CGSWNHP_0023",
    "cgsw0030": "CGSWNHP_0024",
    "cgsw0031": "CGSWNHP_0025",
    "cgsw0032": "CGSWNHP_0026",
    "cgsw0033": "CGSWNHP_0027",
    "cgsw0034": "CGSWNHP_0028",
    "cgsw0035": "CGSWNHP_0029",
    "cgsw0036": "CGSWNHP_0030",
    "cgsw0037": "GURUR_56",
    "cgsw0038": "CGSWNHP_0031",
    "cgsw0039": "CGSWNHP_0032",
    "cgsw0040": "CGSWNHP_0033",
    "cgsw0041": "CGSWNHP_0034",
    "cgsw0042": "CGSWNHP_0035",
    "cgsw0043": "CGSWNHP_0036",
    "cgsw0044": "CGSWNHP_0037",
    "cgsw0045": "CGSWNHP_0038",
    "cgsw0046": "CGSWNHP_0039",
    "cgsw0047": "Gandai_58",
    "cgsw0048": "PARSWANI_009",
    "cgsw0049": "CGSWNHP_0040",
    "cgsw0050": "KOTA_023",
    "cgsw0051": "CGSWNHP_0041",
    "cgsw0052": "AMDI_006",
    "cgsw0053": "DEOKAR_017",
    "cgsw0054": "GOREGHAT_019",
    "cgsw0055": "JAMGAON_004",
    "cgsw0056": "CGSWNHP_0042",
    "cgsw0057": "CGSWNHP_0043",
    "cgsw0058": "CGSWNHP_0044",
    "cgsw0059": "CGSWNHP_0045",
    "cgsw0060": "CGSWNHP_0046",
    "cgsw0062": "CGSW0062",
    "cgsw0062a": "CGSW0062A",
    "cgsw0063": "CGSW0063",
    "cgsw0063a": "CGSW0063A",
    "cgsw0064": "Gondly_56",
    "cgsw0065": "CGSWNHP_0049",
    "cgsw0150": "CGSWNHP_0134",
    "cgsw0068": "CGSWNHP_0052",
    "cgsw0069": "CGSWNHP_0053",
    "cgsw0070": "CGSW0070",
    "cgsw0070a": "CGSW0070A",
    "cgsw0071": "CGSWNHP_0055",
    "cgsw0072": "CGSWNHP_0056",
    "cgsw0073a": "CGSW0073A",
    "cgsw0073b": "CGSW0073B",
    "cgsw0074": "CGSWNHP_0058",
    "cgsw0075": "CGSWNHP_0059",
    "cgsw0076": "CGSWNHP_0060",
    "cgsw0077": "CGSWNHP_0061",
    "cgsw0078": "CGSWNHP_0062",
    "cgsw0079": "CGSWNHP_0063",
    "cgsw0080": "CGSWNHP_0064",
    "cgsw0081": "CGSWNHP_0065",
    "cgsw0082": "CGSWNHP_0066",
    "cgsw0083": "CGSWNHP_0067",
    "cgsw0084": "CGSWNHP_0068",
    "cgsw0085": "CGSWNHP_0069",
    "cgsw0086": "CGSWNHP_0070",
    "cgsw0087": "CGSWNHP_0071",
    "cgsw0088": "CGSWNHP_0072",
    "cgsw0089": "CGSWNHP_0073",
    "cgsw0090": "CGSWNHP_0074",
    "cgsw0091": "CGSWNHP_0075",
    "cgsw0092": "CGSWNHP_0076",
    "cgsw0093": "CGSWNHP_0077",
    "cgsw0094": "CGSWNHP_0078",
    "cgsw0095": "CGSWNHP_0079",
    "cgsw0096": "CGSWNHP_0080",
    "cgsw0097a": "CGSW0097A",
    "cgsw0097b": "CGSW0097B",
    "cgsw0097c": "CGSW0097C",
    "cgsw0097d": "CGSW0097D",
    "cgsw0097e": "CGSW0097E",
    "cgsw0097f": "CGSW0097F",
    "cgsw0098": "CGSWNHP_0082",
    "cgsw0099": "CGSWNHP_0083",
    "cgsw0100": "CGSWNHP_0084",
    "cgsw0101": "CGSWNHP_0085",
    "cgsw0102": "CGSWNHP_0086",
    "cgsw0103": "CGSWNHP_0087",
    "cgsw0104": "CGSWNHP_0088",
    "cgsw0105": "CGSWNHP_0089",
    "cgsw0106": "CGSWNHP_0090",
    "cgsw0107": "CGSWNHP_0091",
    "cgsw0108": "CGSWNHP_0092",
    "cgsw0109": "CGSWNHP_0093",
    "cgsw0110": "CGSWNHP_0094",
    "cgsw0111": "CGSWNHP_0095",
    "cgsw0112": "CGSWNHP_0096",
    "cgsw0113": "CGSWNHP_0097",
    "cgsw0114": "CGSWNHP_0098",
    "cgsw0115": "CGSWNHP_0099",
    "cgsw0116": "CGSWNHP_0100",
    "cgsw0117": "CGSWNHP_0101",
    "cgsw0118": "CGSWNHP_0102",
    "cgsw0119": "CGSWNHP_0103",
    "cgsw0120": "CGSWNHP_0104",
    "cgsw0121": "CGSWNHP_0105",
    "cgsw0122": "CGSWNHP_0106",
    "cgsw0123": "CGSWNHP_0107",
    "cgsw0124": "CGSWNHP_0108",
    "cgsw0125": "CGSWNHP_0109",
    "cgsw0126": "CGSWNHP_0110",
    "cgsw0127": "CGSWNHP_0111",
    "cgsw0128": "CGSWNHP_0112",
    "cgsw0129": "CGSWNHP_0113",
    "cgsw0130": "CGSWNHP_0114",
    "cgsw0131": "CGSWNHP_0115",
    "cgsw0132": "CGSWNHP_0116",
    "cgsw0133": "CGSWNHP_0117",
    "cgsw0134": "CGSWNHP_0118",
    "cgsw0135": "CGSWNHP_0119",
    "cgsw0136": "CGSWNHP_0120",
    "cgsw0137": "CGSWNHP_0121",
    "cgsw0138": "CGSWNHP_0122",
    "cgsw0139": "CGSWNHP_0123",
    "cgsw0140": "CGSWNHP_0124",
    "cgsw0141": "CGSWNHP_0125",
    "cgsw0142": "CGSWNHP_0126",
    "cgsw0143": "CGSWNHP_0127",
    "cgsw0144": "CGSWNHP_0128",
    "cgsw0145": "CGSWNHP_0129",
    "cgsw0146": "CGSWNHP_0130",
    "cgsw0147": "CGSWNHP_0131",
    "cgsw0148": "CGSWNHP_0132",
    "cgsw0149": "CGSWNHP_0133",
}

def get_rgb():
    h, s, l = random.random(), 0.5 + random.random() / 2.0, 0.4 + random.random() / 5.0
    r, g, b = [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]
    return 'rgb(%d,%d,%d)' % (r, g, b)


class Dashboard(View):
    def get(self, request):
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

def download_report(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="site_report.xlsx"'
    startdate = '2023-02-06'
    enddate = '2023-02-07'

    wb = Workbook()
    style = xlwt.easyxf('font: bold 1')
    live = xlwt.easyxf('font: bold 1, color green;')
    delay = xlwt.easyxf('font: bold 1, color orange;')
    offline = xlwt.easyxf('font: bold 1, color red;')
    # add_sheet is used to create sheet.
    sheet1 = wb.add_sheet('Sheet 1')
    sheet1.write(0, 0, 'DATE :', style)
    sheet1.write(0, 1, f'{startdate} - {enddate}')

    counter = 2
    sites = Site.objects.all().order_by('name')
    for site in sites:
        sheet1.write(counter, 0, 'Site Name', style)
        sheet1.write(counter, 1, 'WIMS Code', style)
        sheet1.write(counter, 2, 'Status', style)
        counter = counter + 1
        sheet1.write(counter, 0, site.name.capitalize())
        sheet1.write(counter, 1, NHP.get(site.prefix.lower(),'-'))
        if(site.status == 'Live'):
            sheet1.write(counter, 2, site.status, live)
        elif(site.status == 'Delay'):
            sheet1.write(counter, 2, site.status, delay)
        else:
            sheet1.write(counter, 2, site.status, offline)

        counter = counter + 1
        col = 1
        readingobj = Reading.objects.filter(site=site, timestamp__range=[startdate, enddate]).order_by('timestamp')
        if(readingobj.count() > 0):
            sheet1.write(counter, 0, 'Timestamp', style)
        # print('readingobj >>>> ',readingobj, readingobj.count())
        # df = pd.DataFrame.from_records(list(Reading.objects.filter(site=site, timestamp__range=[startdate, enddate]).values('timestamp', 'reading')))
        # df['data'] = df['reading'].apply(eval)
        # print('df >> ',df)
        if(readingobj.count() > 0):
            param_count = []
            for i in eval(site.parameters):
                param_count.append(i.lower())
                sheet1.write(counter, col, i.capitalize(), style)
                col = col + 1

            for read in readingobj:
                counter = counter + 1
                sheet1.write(counter, 0, str(read.timestamp))
                readings = eval(read.reading)
                par_col = 1
                for parms in param_count:
                    try:
                        sheet1.write(counter, par_col, str(readings[parms]))
                    except:
                        sheet1.write(counter, par_col, str(' '))
                    par_col = par_col + 1



            counter = counter + 3
        else:
            counter = counter + 1

        # if counter >= 50:
        #     break

    wb.save(response)
    return response



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