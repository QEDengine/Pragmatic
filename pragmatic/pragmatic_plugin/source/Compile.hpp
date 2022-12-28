#pragma once

#include "clang/Frontend/FrontendAction.h"
#include "clang/Frontend/CompilerInstance.h"

#include "LanguageOptions.hpp"

namespace QED { namespace Pragmatic
{
	bool Compile(clang::CompilerInvocation& compilerInvocation);

	class RecompileConsumer : public clang::ASTConsumer
	{
		public:
		RecompileConsumer(clang::CompilerInstance& CI);

		private:
		clang::CompilerInstance& CI;

		public:
		void HandleTranslationUnit(clang::ASTContext& context) override;
	};

	class RecompileAction : public clang::PluginASTAction
	{
		public:
		std::unique_ptr<clang::ASTConsumer> CreateASTConsumer(clang::CompilerInstance &CI, llvm::StringRef) override;
		bool ParseArgs(const clang::CompilerInstance &CI, const std::vector<std::string> &args) override;
		clang::PluginASTAction::ActionType getActionType() override;
	};
}} // namespace QED::Pragmatic