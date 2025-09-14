from flask import Flask, request, jsonify , render_template
from .routes import line_item_routes, expresso_details_routes ,dsd_download_routes, dsd_vs_expresso_routes  # adjust path based on your structure
from src.line_item_details.expresso import fetch_full_expresso_details
from src.DSD.parser import extract_til_and_geo_rowwise
from src.DSD.download import Dsd_Download
from src.api.utils import parse_date
def create_app():
    app = Flask(__name__)

    app.register_blueprint(line_item_routes)
    app.register_blueprint(dsd_download_routes)
    app.register_blueprint(expresso_details_routes)
    app.register_blueprint(dsd_vs_expresso_routes)
    @app.route("/")
    def home():
        return "App is running!"
    @app.route("/combined_data_api", methods=["GET"])
    def combined_data_api():
        # Read common query params
        lineitem_name = request.args.get("lineitem_name")
        expresso = lineitem_name[:6]
       
        if not lineitem_name:
            return jsonify({"error": "Missing 'lineitem_name' parameter"}), 400
        if not expresso:
            return jsonify({"error": "Missing 'expresso' parameter"}), 400

        # Call internal logic
        line_item_data = fetch_full_expresso_details(lineitem_name=lineitem_name)
        
        dsd_result = Dsd_Download(expresso)
        expresso_data = extract_til_and_geo_rowwise()
        
        return jsonify({
            "line_item_data": line_item_data,
            "expresso_data": expresso_data,
            "dsd_result": f"DSD Downloaded for {expresso} id" if dsd_result else f"DSD Not Found for {expresso} id" 
        })
    
    @app.route("/combined_data_view", methods=["GET"])
    def combined_data_view():
        lineitem_name = request.args.get("lineitem_name")
        if not lineitem_name:
            return "Missing 'lineitem_name' parameter", 400
        def clean_line_item_name(name):
            while len(name) >= 5 and not name[-5:].isdigit():
                name = name[:-1]
            return name
        expresso = lineitem_name[:6]
        name = clean_line_item_name(lineitem_name)
        # Fetch data like in the API
        line_item_data = fetch_full_expresso_details(lineitem_name=name)
        #dsd_result = Dsd_Download(expresso)
        expresso_data = extract_til_and_geo_rowwise()
        line_item_date = parse_date(line_item_data[0].get("lineitem_start_date"))
        package_name = None
        for item in expresso_data:
            if item["package_name"] == line_item_data[0].get("package_name"):
                package_name = item.get("package_name")
                print(line_item_data[0].get("package_name"))
                print("package name matched")
            dsd_date = parse_date(item.get("Start Date"))

            if dsd_date == line_item_date:
                print("Date matched")
                #print(f"{dsd_date}=={line_item_date}")
            else:
                print("date not matched")
                print(f"{dsd_date}=={line_item_date}")
            break
        # Render the template and pass the data
        return render_template(
            "combined_data.html",
            line_item_data=line_item_data,
            expresso_data=expresso_data,
            #dsd_result=dsd_result,
            expresso=expresso
        )
    return app
    

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)