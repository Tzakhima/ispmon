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
    {%- if data['packet_loss_rate'] is number %}
ispmon:pacekt_loss_percent{ unique_id= "{{ metric['unique_id'] }}", country="{{ metric['country'] }}", isp= "{{ metric['isp'] }}", destination = "{{  destination  }}" }  {{ data['packet_loss_rate'] }}
    {%- endif %}
    {%- if data['packet_loss_count'] is number %}
ispmon:packet_loss_count{ unique_id= "{{ metric['unique_id'] }}", country= "{{ metric['country'] }}", isp= "{{ metric['isp'] }}", destination = "{{  destination  }}" }  {{ data['packet_loss_count'] }}
    {%- endif %}
    {%- if data['rtt_avg'] is number %}
ispmon:rtt_avg{ unique_id= "{{ metric['unique_id'] }}", country= "{{ metric['country'] }}", isp= "{{ metric['isp'] }}", destination = "{{  destination  }}" }  {{ data['rtt_avg'] }}
    {%- endif %}
    {%- if data['packet_transmit'] is number %}
ispmon:packet_transmit{ unique_id= "{{ metric['unique_id'] }}", country= "{{ metric['country'] }}", isp= "{{ metric['isp'] }}", destination = "{{  destination  }}" }  {{ data['packet_transmit'] }}
    {%- endif %}
    {%- if data['packet_receive'] is number %}
ispmon:packet_receive{ unique_id= "{{ metric['unique_id'] }}", country= "{{ metric['country'] }}", isp= "{{ metric['isp'] }}", destination = "{{  destination  }}" }  {{ data['packet_receive'] }}
    {%- endif %}
    {%- endfor %}
    {%- if metric['speed']['available'] == true %}
    {%- if metric['speed']['results']['download'] is number %}
ispmon:speed_download{ unique_id= "{{ metric['unique_id'] }}", country="{{ metric['country'] }}", isp= "{{ metric['isp'] }}" } {{ metric['speed']['results']['download'] }}
    {%- endif %}
    {%- if metric['speed']['results']['upload'] is number %}
ispmon:speed_upload{ unique_id= "{{ metric['unique_id'] }}", country="{{ metric['country'] }}", isp= "{{ metric['isp'] }}" } {{ metric['speed']['results']['upload'] }}
    {%- endif %}
    {%- endif %}
    {%- endfor %}
    '''
    metric_template = Template(template)
    return metric_template.render(metrics=d_data)


app.run(port=8080, host='0.0.0.0')
