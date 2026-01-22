from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from threading import Lock
from scheduler import load_config, build_scheduler, schedule_job, get_scheduler_instance, set_scheduler_instance
from pytz import timezone
import yaml

app = Flask(__name__)
CONFIG_FILE = "config.yaml"
config_lock = Lock()

# Enable error logging
import logging
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

def ensure_config_exists():
    """Ensure config.yaml exists with default structure"""
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            'timezone': 'America/Los_Angeles',
            'jobs': []
        }
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)

def load_config_data():
    """Load configuration from YAML file"""
    with config_lock:
        ensure_config_exists()
        try:
            return load_config(CONFIG_FILE)
        except Exception as e:
            # If config is invalid, return default
            app.logger.error(f"Error loading config: {e}")
            return {
                'timezone': 'America/Los_Angeles',
                'jobs': []
            }

def save_config_data(config):
    """Save configuration to YAML file"""
    import yaml
    with config_lock:
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

@app.route('/')
def index():
    """Main page showing all scheduled jobs"""
    try:
        config = load_config_data()
        jobs = config.get('jobs', [])
        # Ensure hour and minute are integers for template formatting
        for job in jobs:
            if 'schedule' in job:
                if 'hour' in job['schedule']:
                    job['schedule']['hour'] = int(job['schedule']['hour'])
                if 'minute' in job['schedule']:
                    job['schedule']['minute'] = int(job['schedule']['minute'])
        return render_template('index.html', jobs=jobs, timezone=config.get('timezone', 'America/Los_Angeles'))
    except Exception as e:
        app.logger.error(f"Error in index route: {e}")
        return f"Error loading page: {str(e)}", 500

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all scheduled jobs"""
    try:
        config = load_config_data()
        return jsonify(config.get('jobs', []))
    except Exception as e:
        app.logger.error(f"Error getting jobs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<job_name>', methods=['GET'])
def get_job(job_name):
    """Get a scheduled job"""
    config = load_config_data()
    job = next((job for job in config.get('jobs', []) if job['name'] == job_name), None)
    return jsonify(job)

@app.route('/api/jobs', methods=['POST'])
def create_job():
    """Create a new scheduled job"""
    data = request.json
    config = load_config_data()
    
    # Validate required fields
    required_fields = ['name', 'action', 'ticker', 'quantity', 'schedule']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if name already exists
    if any(job['name'] == data['name'] for job in config.get('jobs', [])):
        return jsonify({'error': f'Job with name "{data["name"]}" already exists'}), 400
    
    # Add new job
    if 'jobs' not in config:
        config['jobs'] = []
    config['jobs'].append(data)
    save_config_data(config)
    
    # Update scheduler
    scheduler = get_scheduler_instance()
    if scheduler:
        tz = timezone(config.get('timezone', 'America/Los_Angeles'))
        schedule_job(scheduler, data, tz)
    
    return jsonify(data), 201

@app.route('/api/jobs/<job_name>', methods=['PUT'])
def update_job(job_name):
    """Update an existing scheduled job"""
    data = request.json
    config = load_config_data()
    
    # Find and update job
    jobs = config.get('jobs', [])
    job_index = None
    for i, job in enumerate(jobs):
        if job['name'] == job_name:
            job_index = i
            break
    
    if job_index is None:
        return jsonify({'error': f'Job "{job_name}" not found'}), 404
    
    # Update job data
    jobs[job_index].update(data)
    jobs[job_index]['name'] = job_name  # Ensure name doesn't change
    save_config_data(config)
    
    # Update scheduler
    scheduler = get_scheduler_instance()
    if scheduler:
        tz = timezone(config.get('timezone', 'America/Los_Angeles'))
        schedule_job(scheduler, jobs[job_index], tz)
    
    return jsonify(jobs[job_index])

@app.route('/api/jobs/<job_name>', methods=['DELETE'])
def delete_job(job_name):
    """Delete a scheduled job"""
    config = load_config_data()
    
    # Find and remove job
    jobs = config.get('jobs', [])
    job_index = None
    for i, job in enumerate(jobs):
        if job['name'] == job_name:
            job_index = i
            break
    
    if job_index is None:
        return jsonify({'error': f'Job "{job_name}" not found'}), 404
    
    deleted_job = jobs.pop(job_index)
    save_config_data(config)
    
    # Remove from scheduler
    scheduler = get_scheduler_instance()
    if scheduler:
        try:
            scheduler.remove_job(job_name)
        except:
            pass  # Job might not exist in scheduler
    
    return jsonify({'message': f'Job "{job_name}" deleted'}), 200

@app.route('/api/timezone', methods=['GET'])
def get_timezone():
    """Get current timezone"""
    config = load_config_data()
    return jsonify({'timezone': config.get('timezone', 'America/Los_Angeles')})

@app.route('/api/timezone', methods=['PUT'])
def update_timezone():
    """Update timezone"""
    data = request.json
    if 'timezone' not in data:
        return jsonify({'error': 'Missing timezone field'}), 400
    
    config = load_config_data()
    config['timezone'] = data['timezone']
    save_config_data(config)
    
    # Rebuild scheduler with new timezone
    scheduler = get_scheduler_instance()
    if scheduler:
        from scheduler import rebuild_scheduler
        rebuild_scheduler(config)
    
    return jsonify({'timezone': config['timezone']})

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        config = load_config_data()
        scheduler = get_scheduler_instance()
        return jsonify({
            'status': 'healthy',
            'config_exists': os.path.exists(CONFIG_FILE),
            'scheduler_running': scheduler is not None,
            'jobs_count': len(config.get('jobs', []))
        }), 200
    except Exception as e:
        app.logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
