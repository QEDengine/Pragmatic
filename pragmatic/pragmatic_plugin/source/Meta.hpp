#pragma once

// Standard library
#include <string>
#include <map>
// Clang
#include "clang/Basic/Diagnostic.h"
#include "clang/Lex/Preprocessor.h"
#include "clang/Serialization/ModuleFileExtension.h"
// Exteral
#include <nlohmann/json.hpp>
using json = nlohmann::ordered_json;

namespace QED::Pragmatic
{
	struct Option
	{
		std::string value;
	};
	NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE_WITH_DEFAULT(Option, value);

	struct Node
	{
		std::string path;
		std::vector<std::string> defines;

		std::map<std::string, Option> options;
	};

	struct Edge
	{
		std::string source;
		std::string target;
		std::string relation;
		std::vector<std::string> defines;

		std::vector<Option> options;
	};

	struct Meta
	{
		private:
		Meta() = default;
		public:
		static Meta& Instance();
		Meta(Meta const&) = delete;
        void operator=(Meta const&) = delete;
		~Meta() = default;

		nlohmann::ordered_json& operator[](const std::string& key);
        nlohmann::ordered_json::iterator begin();
        nlohmann::ordered_json::iterator end();

		static struct Node& Node(std::string path, std::string defined);
		static struct Edge& Edge(std::string source, std::string target, std::string relation, std::string defined);

		private:
		::json GeneratePatchesForNodes();
		::json GeneratePatchesForEdges();

		public:
		void Write(clang::Preprocessor& preprocessor, bool exit=false);
		
		private:
		std::string metaFilePath;
		json json = {};
		std::vector<struct Node> nodes;
		std::vector<struct Edge> edges;

	};

} // namesapce QED::Pragmatic