// Source header
#include "Meta.hpp"
// Standard library
#include <string>
#include <algorithm>
#include <fstream>
#include <filesystem>
#include <iomanip>
#include <functional> 
#include <sstream>
// Pragmatic
#include "Utility.hpp"
#include "nlohmann/json.hpp"
#include "llvm/Support/raw_ostream.h"

using namespace nlohmann::literals;

const ::json inital_json =
R"(
{
	"graphs":
	[
		{
			"nodes":{},
			"edges":[]
		}
	]
})"_json;

namespace
{
	bool Contains(const json& array, std::string element)
	{
		if (array == nullptr || array.size() == 0) return false;
		for (auto& item : array)
			if (item == element) return true;
		return false;
	}

	bool Contains(const json& array, std::function<bool(const json&)> condition)
	{
		if (array == nullptr || array.size() == 0) return false;
		for (auto& item : array)
			if (condition(item)) return true;
		return false;
	}

	void RemoveNulls(::json& json)
	{
		for (auto it = json.begin(); it != json.end();)
		{
			if (it.value().is_null())
				it = json.erase(it);
			else if(it.value().is_object() || it.value().is_array())
			{
				RemoveNulls(it.value());
				++it;
			}
			else ++it;
		}
	}

	std::vector<std::string> GetNodePaths(std::vector<QED::Pragmatic::Node>& nodes)
	{
		auto names = std::vector<std::string>();
		for(auto& node : nodes)
			names.emplace_back(node.path);

		return names;
	}

	bool MatchPath(std::vector<QED::Pragmatic::Node>& nodes, std::string match)
	{
		auto paths = GetNodePaths(nodes);
		return std::find_if(paths.begin(), paths.end(), [&match](const std::string& path) -> bool { return path == match; }) != paths.end();
	}

	QED::Pragmatic::Node& GetNode(std::vector<QED::Pragmatic::Node>& nodes, std::string path)
	{
		for (auto& node : nodes)
		{
			if (node.path == path)
				return node;
		}

		throw new std::exception("Tried to find node with incorrect path");
	}

	bool MatchEdge(std::vector<QED::Pragmatic::Edge>& edges, std::string source, std::string target, std::string relation)
	{
		return std::find_if(edges.begin(), edges.end(), [&source, &target, &relation](const QED::Pragmatic::Edge& edge) -> bool
		{
			return edge.source == source && edge.target == target && edge.relation == relation;
			}) != edges.end();
	}

	QED::Pragmatic::Edge& GetEdge(std::vector<QED::Pragmatic::Edge>& edges, std::string source, std::string target, std::string relation)
	{
		for (auto& edge : edges)
		{
			if (edge.source == source && edge.target == target && edge.relation == relation)
				return edge;
		}

		throw new std::exception("Tried to find node with incorrect path");
	}
}

namespace QED::Pragmatic
{
	Meta& Meta::Instance()
	{
		static Meta instance;
		if (instance.json.empty())
			instance.json = inital_json;

		return instance;
	}

	nlohmann::ordered_json& Meta::operator[](const std::string& key)
	{
		return json["graphs"][0][key];
	}

	nlohmann::ordered_json::iterator Meta::begin()
	{
		return json.begin();
	}

	nlohmann::ordered_json::iterator Meta::end()
	{
		return json.end();
	}

	void Meta::Node(std::string path, std::string defined, std::string standard)
	{
		auto& meta = Instance();
		// Check if there is already a node defined at path
		bool found = false;
		for (auto& node : meta.nodes)
		{
			// There is a node with the same path
			if (node.path == path)
			{
				auto& defines = node.defines;
				// Add new define if not already there
				if (std::find_if(defines.begin(), defines.end(), [&defined](const std::string& nodeDefine) -> bool
				{
					return nodeDefine == defined;
				}) == defines.end())
					defines.push_back(defined);

				if (standard != "")
					node.standard = standard;

				found = true;
				break;
			}
		}

		if (!found)
			meta.nodes.push_back((struct Node){path, {defined}, standard});
	}

	void Meta::Edge(std::string source, std::string target, std::string relation, std::string defined)
	{
		auto& meta = Instance();
		// Check if there is already an edge defined with same source, target & relation
		bool found = false;
		for (auto& edge : meta.edges)
		{
			// There is an edge with the same source, target & relation
			if (edge.source == source && edge.target == target && edge.relation == relation)
			{
				auto& defines = edge.defines;
				// Add new define if not already there
				if (std::find_if(defines.begin(), defines.end(), [&defined](const std::string& nodeDefine) -> bool
				{
					return nodeDefine == defined;
				}) == defines.end())
					defines.push_back(defined);

				found = true;
				break;
			}
		}

		if (!found)
			meta.edges.push_back((struct Edge){source, target, relation, {defined}});
	}

	::json Meta::GeneratePatchesForNodes()
	{
		::json patches = ::json::array();
		auto& jsonNodes = json["graphs"][0]["nodes"];

		// Add new nodes
		for (auto& node : nodes)
		{
			if (!jsonNodes.contains(node.path))
			{
				auto nodeObject = ::json::object();
				nodeObject["metadata"]["defined"] = ::json::array();
				for (auto& define : node.defines)
					nodeObject["metadata"]["defined"].push_back(define);
				patches.push_back({{"op", "add"}, {"path", "/graphs/0/nodes/" + node.path}, {"value", nodeObject}});
			}
		}

		// Apply new nodes patch
		json.patch_inplace(patches);

		// Iterate over nodes & generate changes patch
		for (auto it = jsonNodes.begin(); it != jsonNodes.end(); ++it)
		{
			auto &current = *it;
			auto &metadata = current["metadata"];
			auto &defines = metadata["defined"];

			std::vector<std::string> defintionsToRemove;
			for (int i = 0; i < defines.size(); i++)
			{
				// Remove nodes that are defined by a currently handled file in the metafile, but not longer is
				auto &defined = defines[i];
				if (MatchPath(nodes, defined) && !MatchPath(nodes, it.key()))
				{
					defintionsToRemove.emplace_back(defined);
					defines.erase(i);
				}
			}

			// Create definition removal patches
			if (defines.empty())
				patches.push_back({{"op", "remove"}, {"path", "/graphs/0/nodes/" + it.key()}});
			else
				for (auto& defintionToRemove : defintionsToRemove)
					patches.push_back({{"op", "remove"}, {"path", "/graphs/0/nodes/" + it.key() + "/metadata/defined/" + defintionToRemove}});

			if (MatchPath(nodes, it.key()))
			{
				auto& node = GetNode(nodes, it.key());
				if (node.standard == "" && metadata.contains("standard"))
					patches.push_back({{"op", "remove"}, {"path", "/graphs/0/nodes/" + it.key() + "/metadata/standard"}});
				else if (node.standard != "" && !metadata.contains("standard"))
					patches.push_back({{"op", "add"}, {"path", "/graphs/0/nodes/" + it.key() + "/metadata/standard"}, {"value", node.standard}});
				else if (metadata.contains("standard") && node.standard != metadata["standard"])
					patches.push_back({{"op", "replace"}, {"path", "/graphs/0/nodes/" + it.key() + "/metadata/standard"}, {"value", node.standard}});
			}
		}

		return patches;
	}

	::json Meta::GeneratePatchesForEdges()
	{
		::json patches = ::json::array();
		auto workingJson = json;
		auto& jsonEdges = workingJson["graphs"][0]["edges"];

		// Add new edges
		for (auto& edge : edges)
		{
			if (std::find_if(jsonEdges.begin(), jsonEdges.end(), [&edge](::json& jsonEdge) -> bool
			{
				return jsonEdge["source"] == edge.source && jsonEdge["target"] == edge.target && jsonEdge["relation"] == edge.relation;
			}) == jsonEdges.end())
			{
				auto edgeObject = ::json::object();
				edgeObject["source"] = edge.source;
				edgeObject["target"] = edge.target;
				edgeObject["relation"] = edge.relation;
				edgeObject["metadata"]["defined"] = ::json::array();
				for (auto& define : edge.defines)
					edgeObject["metadata"]["defined"].emplace_back(define);

				patches.push_back({{"op", "add"}, {"path", "/graphs/0/edges/-"}, {"value", edgeObject}});
			}
		}

		// Apply new edges patch
		workingJson.patch_inplace(patches);

		// Iterate over edges & generate changes patch
		for (auto it = jsonEdges.begin(); it != jsonEdges.end(); ++it)
		{
			auto &current = *it;
			auto &metadata = current["metadata"];
			auto &defines = metadata["defined"];

			std::vector<std::string> defintionsToRemove;
			for (int i = 0; i < defines.size(); i++)
			{
				// Remove edges that are defined by a currently handled file in the metafile, but not longer is
				auto &defined = defines[i];
				if (MatchPath(nodes, defined) && !MatchEdge(edges, current["source"], current["target"], current["relation"]))
				{
					defintionsToRemove.emplace_back(defined);
					defines.erase(i);
				}
			}

			auto indexStr = std::to_string(std::distance(jsonEdges.begin(), it));

			// Create definition removal patches
			if (defines.empty())
				patches.push_back({{"op", "remove"}, {"path", "/graphs/0/edges/" + indexStr}});
			else
				for (auto& defintionToRemove : defintionsToRemove)
					patches.push_back({{"op", "remove"}, {"path", "/graphs/0/edges/" + indexStr + "/metadata/defined/" + defintionToRemove}});
		}

		return patches;
	}

	void Meta::Write(clang::Preprocessor& preprocessor, bool exit)
	{
		metaFilePath = (GetMacroValue(preprocessor, "PRAGMATIC_FILE_PATH"));
		
		std::ifstream sourceFileJson(metaFilePath);
		// If file doesn't exitst, create one
		if (!sourceFileJson)
		{
			std::ofstream o(metaFilePath);
			o << std::setw(4) << inital_json << std::endl;
			o.close();
			sourceFileJson = std::ifstream(metaFilePath);
		}

		// Read source file JSON
		sourceFileJson >> json;

		auto nodePatch = GeneratePatchesForNodes();
		auto edgePatch = GeneratePatchesForEdges();

		// Apply changes
		json.patch_inplace(nodePatch);
		json.patch_inplace(edgePatch);

		// Save metafile
		std::ofstream o(metaFilePath);
		o << std::setw(4) << json << std::endl;
		o.close();

		// Print patch
		std::stringstream ss;
		ss << std::setw(4) << nodePatch << '\n';
		ss << std::setw(4) << edgePatch;
		llvm::outs() << ss.str();

		// Exit if explicitly told so
		if (exit) ::exit(42);
	}
} // namesapce QED::Pragmatic