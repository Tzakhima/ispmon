import flask
import redis
import pickle
from jinja2 import Template


# Flask Parameters
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Redis
message_r = redis.Redis(host='localhost', port=6379, db=0)


@app.route('/metrics', methods=['get'])
def get_metrics():
    data = message_r.lrange('metrics', 0, -1)
    message_r.delete('metrics')
    # decode
    d_data = []
    for x in data:
        d_data.append(pickle.loads(x))
    print(d_data)
    template = '''
    {%- for metric in metrics %}
    {%- for destination, data in metric['ping'].items() %}
ispmon:pacekt_loss_percent{ unique_id= "{{ metric['unique_id'] }}", country="{{ metric['country'] }}", isp= "{{ metric['isp'] }}", destination = "{{  destination  }}" }  {{ data['packet_loss_rate'] if data['packet_loss_rate'] != None else 0 }}
ispmon:rtt_avg{ unique_id= "{{ metric['unique_id'] }}", country= "{{ metric['country'] }}", isp= "{{ metric['isp'] }}", destination = "{{  destination  }}" }  {{ data['rtt_avg'] if data['rtt_avg'] != None else 0}}
    {%- endfor %}
    {%- if metric['speed']['available'] == true %}
ispmon:speed_download{ unique_id= "{{ metric['unique_id'] }}", country="{{ metric['country'] }}", isp= "{{ metric['isp'] }}" } {{ metric['speed']['results']['download']  if metric['speed']['results']['download'] != None else 0 }}
ispmon:speed_upload{ unique_id= "{{ metric['unique_id'] }}", country="{{ metric['country'] }}", isp= "{{ metric['isp'] }}" } {{ metric['speed']['results']['upload'] if metric['speed']['results']['upload'] != None else 0 }}
    {%- endif %}
    {%- endfor %}
    '''
    metric_template = Template(template)
    return metric_template.render(metrics=d_data)


app.run(port=8080, host='0.0.0.0')
