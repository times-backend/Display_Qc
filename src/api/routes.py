from flask import Blueprint, request, jsonify, render_template
from src.line_item_details.expresso import fetch_full_expresso_details
from src.DSD.parser import extract_til_and_geo_rowwise
from src.DSD.download import Dsd_Download
from src.helper.dsd_vs_expresso import dsd_vs_expresso , finalData_vs_gamData

line_item_routes = Blueprint("line_item_routes", __name__)
expresso_details_routes = Blueprint("expresso_details_routes", __name__)
dsd_download_routes = Blueprint("dsd_download_routes", __name__)
dsd_vs_expresso_routes = Blueprint("dsd_vs_expresso_routes", __name__)

@line_item_routes.route("/line_item_details_api", methods=["GET"])
def line_item_details_api():
    lineitem_name = request.args.get("lineitem_name")
    if not lineitem_name:
        return jsonify({"error": "Missing 'lineitem_name' parameter"}), 400

    data = fetch_full_expresso_details(lineitem_name=lineitem_name)
    return jsonify(data)


@expresso_details_routes.route("/expresso_details_api", methods=["GET"])
def expresso_details_api():
    #lineitem_name = request.args.get("lineitem_name")
    #if not lineitem_name:
    #    return jsonify({"error": "Missing 'lineitem_name' parameter"}), 400

    data = extract_til_and_geo_rowwise()
    return jsonify(data)

@dsd_download_routes.route("/dsd_download_api", methods=["GET"])
def dsd_download_api():
    expresso = request.args.get("expresso")
    print(expresso)
    if not expresso:
        return jsonify({"error": "Missing 'expresso' parameter"}), 400
    data = Dsd_Download(expresso)
    return jsonify({"message": f"DSD Downloaded for {expresso} id"})

@dsd_vs_expresso_routes.route("/compare", methods=["GET", "POST"])
def compare_ui():
    result = None
    error = None
    gam_comparison = None

    if request.method == "POST":
        lineitem_name = request.form.get("lineitem_name")

        if not lineitem_name:
            error = "Please provide a line item name."
        else:
            # First: Compare DSD vs Expresso
            result_data, status_code = dsd_vs_expresso(lineitem_name)
            if status_code == 200:
                result = result_data
            else:
                error = result_data.get("error", "Unknown error")
                return render_template("expresso_vs_dsd.html", result=None, gam_comparison=None, error=error)

            # Second: Compare Final Data vs GAM
            try:
                gam_data_result = finalData_vs_gamData(lineitem_name)

                # Structure gam_comparison so that template gets fields, extra_info, and matched_gam
                raw_comparison = gam_data_result.get("comparison", {})
                gam_comparison = {}

                for key, comp in raw_comparison.items():
                    gam_comparison[key] = {
                        "fields": comp.get("fields", {}),
                        "extra_info": comp.get("extra_info", {}),
                        "matched_gam": comp.get("matched_gam", {})
                    }

            except Exception as e:
                error = f"Error during GAM comparison: {str(e)}"

    return render_template(
        "expresso_vs_dsd.html",
        result=result,
        gam_comparison=gam_comparison,
        error=error
    )


@dsd_vs_expresso_routes.route("/final-vs-gam", methods=["GET"])
def get_final_vs_gam():
    lineitem_name = request.args.get("lineitem_name")
    if not lineitem_name:
        return jsonify({"error": "Missing lineitem_name"}), 400

    try:
        data = finalData_vs_gamData(lineitem_name)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@dsd_vs_expresso_routes.route("/expresso-vs-dsd-api", methods=["POST"])
def api_compare():
    data = request.get_json()
    lineitem_name = data.get("lineitem_name")

    if not lineitem_name:
        return jsonify({"error": "Missing 'lineitem_name' in request body"}), 400

    result, status = dsd_vs_expresso(lineitem_name)
    return jsonify(result), status